from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
import json
import secrets
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

from pathlib import Path

# Define Base Dir (Resolved to Project Root)
# main.py is in devchatbot/backend/ (2 levels deep from root if we consider devchatbot2 as root context, 
# but actually: devchatbot2/devchatbot/backend/main.py -> parent -> backend, parent -> devchatbot, parent -> devchatbot2)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

load_dotenv(dotenv_path=ENV_PATH, override=True)

app = FastAPI(title="DevChatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to update .env file
def update_env_file(key, value):
    env_path = ENV_PATH
    # load existing lines
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    key_found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            key_found = True
        else:
            new_lines.append(line)
    
    if not key_found:
        if new_lines and not new_lines[-1].endswith('\n'):
             new_lines.append('\n')
        new_lines.append(f"{key}={value}\n")
        
    with open(env_path, 'w') as f:
        f.writelines(new_lines)

    # Reload environment immediately
    os.environ[key] = value

# Database Configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'social')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def get_chat_context():
    conn = get_db_connection()
    if not conn:
        return None
    
    context = {'faq': [], 'fasilitas': []}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch FAQ
        cursor.execute("SELECT pertanyaan, jawaban FROM faq")
        context['faq'] = cursor.fetchall()
        
        # Fetch Fasilitas
        cursor.execute("""
            SELECT 
                nama_fasilitas,
                alamat,
                kelurahan,
                kecamatan,
                latitude,
                longitude,
                telp,
                email,
                website
            FROM fasilitas
            ORDER BY nama_fasilitas
        """)
        context['fasilitas'] = cursor.fetchall()

        cursor.execute("""
            SELECT 
                keyword,
                keterangan,
                response
            FROM pelayanan_publik
            ORDER BY keyword
        """)
        context['pelayanan_publik'] = cursor.fetchall()
        
    except mysql.connector.Error as err:
        print(f"Error fetching data: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return context

# Pydantic Models
class SetupRequest(BaseModel):
    geminiKey: str

class ChatRequest(BaseModel):
    apiKey: str
    message: str
    history: List[Dict[str, Any]] = []
    stream: bool = False

@app.post("/api/setup")
async def setup(request: SetupRequest):
    gemini_key = request.geminiKey
    
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required")

    # Generate new Access Token
    new_access_token = f"sk-dev-{secrets.token_hex(4)}"
    
    # Save to .env
    update_env_file("GEMINI_API_KEY", gemini_key)
    update_env_file("SERVER_ACCESS_TOKEN", new_access_token)
    
    return {
        'message': 'Configuration saved successfully',
        'accessToken': new_access_token
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    client_key = request.apiKey
    message = request.message
    history = request.history
    stream = request.stream
    
    # 1. Load Keys from Config File (can be optimized to load once, but for now file read is fast enough or use cache)
    server_gemini_key = os.getenv("GEMINI_API_KEY")
    server_access_token = os.getenv("SERVER_ACCESS_TOKEN")
    


    if not server_access_token or not server_gemini_key:
        raise HTTPException(status_code=503, detail="Server Not Configured.")

    # 2. Authenticate
    if client_key != server_access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not message:
         raise HTTPException(status_code=400, detail="Message is required")

    # 3. Optimized DB Call
    # Use run_in_threadpool to avoid blocking main loop
    context = await run_in_threadpool(get_chat_context)
    if not context:
        raise HTTPException(status_code=500, detail="Failed to fetch system context")

    # --- RELEVANCE FILTER ---
    def extract_keywords(ctx):
        keywords = set()
        # Extract from FAQ
        for item in ctx['faq']:
            # Split question into words and add valid ones (len > 3)
            words = item['pertanyaan'].lower().split()
            keywords.update([w for w in words if len(w) > 3])
        
        # Extract from Fasilitas
        for item in ctx['fasilitas']:
            keywords.add(item['nama_fasilitas'].lower())
            
        # Extract from Pelayanan
        for item in ctx['pelayanan_publik']:
            keywords.add(item['keyword'].lower())
            
        return keywords

    def is_relevant(msg, keywords):
        msg_lower = msg.lower()
        # 1. Direct Keyword Match
        for kw in keywords:
            if kw in msg_lower:
                return True
        
        # 2. General Whitelist (Greeting/Closing)
        whitelist = ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'terima kasih', 'makasih', 'permisi', 'bantuan']
        if any(w in msg_lower for w in whitelist):
            return True
            
        return False

    db_keywords = extract_keywords(context)
    if not is_relevant(message, db_keywords):
        template_response = "Maaf, pertanyaan Anda sepertinya tidak berkaitan dengan data layanan publik, fasilitas, atau informasi Kota Pangkal Pinang yang saya miliki. Silakan ajukan pertanyaan yang lebih spesifik mengenai kota ini."
        
        if stream:
            async def config_generator():
                yield template_response
            return StreamingResponse(config_generator(), media_type="text/plain")
        else:
            return {'text': template_response}
    # ------------------------

    # Format Context
    faq_context = "\n\n".join([f"Q: {item['pertanyaan']}\nA: {item['jawaban']}" for item in context['faq']])
    
    fasilitas_List = []
    for f in context['fasilitas']:
        telp = f['telp'] if f['telp'] else ''
        fasilitas_str = f"{f['nama_fasilitas']}|{f['alamat']}|{f['kelurahan']}|{f['kecamatan']}|{f['email']}|{f['website']}"
        if telp:
            fasilitas_str += f"|{telp}"
        fasilitas_List.append(fasilitas_str)
        
    fasilitas_context = "\n".join(fasilitas_List)

    pelayanan_publik_List = []
    for f in context['pelayanan_publik']:
        # Format: Keyword, Keterangan, and Response (containing HTML/details)
        pelayanan_publik_str = f"Keyword: {f['keyword']}\nKeterangan: {f['keterangan']}\nDetail: {f['response']}\n"
        pelayanan_publik_List.append(pelayanan_publik_str)

    pelayanan_publik_context = "\n---\n".join(pelayanan_publik_List)

    system_instruction = f"""Anda adalah perwakilan ramah dan pemandu lokal Kota Pangkal Pinang. 
Tujuan Anda adalah membantu warga dan pengunjung dengan informasi yang akurat namun disampaikan secara natural, layaknya berbicara dengan manusia, bukan robot.

DATA REFERENSI:

=== FAQ & INFORMASI UMUM ===
{faq_context}

=== FASILITAS & LOKASI DI PANGKAL PINANG ===
Data berikut berisi daftar Fasilitas (Fformat: Nama|Alamat|Kelurahan|Kecamatan|Telp):
{fasilitas_context}

=== PELAYANAN PUBLIK ===
{pelayanan_publik_context}

PRINSIP KOMUNIKASI (SANGAT PENTING):
1. **Dilarang Keras** menggunakan kalimat seperti "Berdasarkan data yang saya miliki", "Menurut informasi saya", atau "Dalam database kami". 
2. Jawablah langsung secara natural. Contoh: Jika ditanya "Apakah Kampak ada di Pangkal Pinang?", jawab "Ya, Kampak itu ada di Pangkal Pinang. Itu adalah nama daerah/jalan yang masuk wilayah Kecamatan Gerunggang."
3. Jika informasi ditemukan di data fasilitas, sampaikan lokasinya dengan akrab. 
4. Jika Anda tidak menemukan data spesifik yang dicari, tetaplah membantu. Jangan langsung menolak. Coba arahkan dengan ramah ke layanan resmi Pemerintah Kota Pangkal Pinang.
5. Gunakan nada bicara yang HANGAT, SOLUTIF, dan PROFESIONAL.
6. Anda adalah wajah dari Kota Pangkal Pinang. Buatlah orang merasa terbantu dan nyaman.
7. Selalu gunakan Bahasa Indonesia yang santun namun tetap komunikatif.
8. **PENTING - BATAS TOKEN**: Anda memiliki kuota kata yang sangat terbatas. **JAWABLAH DENGAN SINGKAT DAN PADAT**.
9. Jika pengguna meminta daftar/list yang hasilnya banyak:
   - HANYA sebutkan **3-5 item** random saja.
   - Jangan berikan deskripsi panjang lebar untuk setiap item.
   - Akhiri list dengan kalimat "...dan masih banyak lagi."
   - Prioritaskan agar jawaban Anda **tidak terpotong**. Lebih baik jawaban pendek tapi utuh daripada panjang tapi terpotong.
10. Ingat: Anda adalah pemandu kota yang cerdas dan ramah, bukan sekadar mesin pencari data."""

    try:
        client = genai.Client(api_key=server_gemini_key)
        
        chat_history = []
        for msg in history:
            role = 'user' if msg.get('role') == 'user' else 'model'
            chat_history.append(types.Content(
                role=role,
                parts=[types.Part(text=msg.get('text', ''))]
            ))
            
        chat_history.append(types.Content(
            role='user',
            parts=[types.Part(text=message)]
        ))

        # STREAMING LOGIC
        if stream:
            async def response_generator():
                response = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        max_output_tokens=500
                    )
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

            return StreamingResponse(
                response_generator(), 
                media_type="text/plain"
            )
        
        # STANDARD LOGIC
        else:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=500
                )
            )
            return {'text': response.text}
        
    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "Welcome to DevChatbot API",
        "docs": "/docs",
        "health": "/api/status"
    }

@app.get("/api/chat")
async def chat_get(apiKey: str, message: str, stream: bool = True):
    """
    GET endpoint for chat. Defaults to stream=True for instant response demo.
    """
    request = ChatRequest(apiKey=apiKey, message=message, stream=stream)
    return await chat(request)

@app.get("/api/status")
async def status():
    return {
        'status': 'online',
        'service': 'DevChatbot API',
        'version': '1.0.0',
        'message': 'Server is running smoothly.'
    }

if __name__ == "__main__":
    import uvicorn
    
    # CLI Setup: Check if keys exist
    gemini_key = os.getenv("GEMINI_API_KEY")
    access_token = os.getenv("SERVER_ACCESS_TOKEN")
    

        
    # If still missing, prompt user
    if not gemini_key:
        print("\n" + "="*50)
        print(" WELCOME TO DEVCHATBOT SETUP")
        print("="*50)
        print("Configuration missing. Please follow the steps below.\n")
        
        gemini_key = input("1. Enter your Gemini API Key: ").strip()
        
        while not gemini_key:
             print("Error: API Key cannot be empty.")
             gemini_key = input("1. Enter your Gemini API Key: ").strip()

        # Generate Access Token
        access_token = f"sk-dev-{secrets.token_hex(4)}"
        
        # Save to .env
        update_env_file("GEMINI_API_KEY", gemini_key)
        update_env_file("SERVER_ACCESS_TOKEN", access_token)
        
        print("\n" + "-"*50)
        print(" SUCCESS! Configuration Saved.")
        print("-"*50)
        print(f"Gemini Key  : {gemini_key[:5]}...{gemini_key[-3:]}")
        print(f"ACCESS KEY  : {access_token}  <-- COPY THIS!")
        print("-"*50 + "\n")
        print("Starting server...\n")
        
    elif not access_token:
        # Rare case: Gemini key exists but access token doesn't (maybe manually edited file)
        access_token = f"sk-dev-{secrets.token_hex(4)}"
        update_env_file("SERVER_ACCESS_TOKEN", access_token)
        print(f"\nGenerared new Access Key: {access_token}\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
