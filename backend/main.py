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

load_dotenv(override=True)

app = FastAPI(title="DevChatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = 'server_config.json'

class ConfigManager:
    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            return {}
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_config(gemini_key, access_token):
        config = {
            "gemini_key": gemini_key,
            "access_token": access_token
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return config

    @staticmethod
    def get_keys():
        config = ConfigManager.load_config()
        return config.get('gemini_key'), config.get('access_token')

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
    
    # Save to file
    ConfigManager.save_config(gemini_key, new_access_token)
    
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
    server_gemini_key, server_access_token = ConfigManager.get_keys()
    


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

    # Determine response type and set token limits
    question = message.lower()
    
    # Default values
    max_tokens = 300  # Increased default token limit
    response_style = ""
    min_tokens = 20   # Ensure minimum response length
    
    # Analyze question type and adjust response parameters
    if any(word in question for word in ['di mana', 'lokasi', 'alamat', 'dimana']):
        response_style = """
        WAJIB ikuti format berikut:
        [NAMA TEMPAT]
        Alamat: [alamat lengkap]
        Kecamatan: [nama kecamatan]
        Koordinat: [jika tersedia]
        Telp: [jika tersedia]
        
        Jika tidak menemukan lokasi yang tepat, berikan lokasi terdekat yang relevan."""
        max_tokens = 200
        min_tokens = 30
        
    elif any(word in question for word in ['jam buka', 'jam operasional', 'buka jam', 'tutup jam']):
        response_style = """
        WAJIB ikuti format:
        [NAMA TEMPAT]
        Jam Operasional: [hari] [waktu buka] - [waktu tutup] WIB
        Contoh: Senin-Jumat 08.00-16.00 WIB
        
        Jika tidak tahu jam operasional, beri tahu dengan jujur."""
        max_tokens = 150
        min_tokens = 20
        
    elif any(word in question for word in ['syarat', 'persyaratan', 'dokumen']):
        response_style = """
        Daftar persyaratan yang LENGKAP:
        1. [Persyaratan 1]
           - Keterangan tambahan
        2. [Persyaratan 2]
        
        Pastikan mencantumkan:
        - Jumlah rangkap dokumen
        - Dokumen asli/fotokopi
        - Masa berlaku dokumen (jika ada)"""
        max_tokens = 400
        min_tokens = 50
        
    elif any(word in question for word in ['cara', 'prosedur', 'tahapan']):
        response_style = """
        Langkah-langkah lengkap:
        1. [Langkah 1]
           - Detail penting
        2. [Langkah 2]
        
        Informasi tambahan:
        - Waktu penyelesaian: [estimasi]
        - Biaya: [jika ada]
        - Lokasi: [tempat pengurusan]"""
        max_tokens = 500
        min_tokens = 60
        
    else:
        response_style = """
        Berikan jawaban yang:
        - Langsung ke inti permasalahan
        - Maksimal 3-4 kalimat
        - Jelas dan mudah dipahami
        - Jika tidak tahu, sarankan kontak yang bisa dihubungi"""
        max_tokens = 200
        min_tokens = 15

    system_instruction = f"""ANDA ADALAH ASISTEN RESMI PEMERINTAH KOTA PANGKAL PINANG

PERINTAH PENTING:
1. WAJIB menjawab dengan format yang diminta
2. JANGAN mengulang pertanyaan dalam jawaban
3. Gunakan BAHASA INDONESIA yang baik dan benar
4. Jika informasi tidak lengkap, beri tahu dengan jujur
5. JANGAN membuat informasi yang tidak ada dalam data

{response_style}

DATA REFERENSI:

=== INFORMASI UMUM ===
{faq_context}

=== FASILITAS ===
{fasilitas_context}

=== LAYANAN PUBLIK ===
{pelayanan_publik_context}

FORMAT STANDAR:
- Tanggal: DD/MM/YYYY
- Waktu: 24 jam (contoh: 14.00 WIB)
- Nomor telepon: +62 [kode area] [nomor]"""

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

        # Common config for both streaming and non-streaming
        generation_config = {
            'model': 'gemini-2.5-flash',
            'contents': chat_history,
            'config': types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1024,  # Increased max tokens
                temperature=0.7,         # Slightly higher for more natural responses
                top_p=0.9,
                top_k=40,
                stop_sequences=['\n\n']  # Stop at double newlines
            )
        }

        # STREAMING LOGIC
        if stream:
            async def response_generator():
                full_response = ""
                response = client.models.generate_content_stream(**generation_config)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        yield chunk.text
                
                # If response was cut off, add ellipsis
                if full_response and not full_response.strip().endswith(('.', '!', '?')):
                    yield '...'

            return StreamingResponse(
                response_generator(), 
                media_type="text/plain"
            )
        
        # STANDARD LOGIC
        else:
            response = client.models.generate_content(**generation_config)
            response_text = response.text.strip()
            
            # Ensure response ends with proper punctuation
            if response_text and not response_text.endswith(('.', '!', '?')):
                response_text += '...'
                
            return {'text': response_text}
        
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
    gemini_key, access_token = ConfigManager.get_keys()
    

        
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
        
        # Save
        ConfigManager.save_config(gemini_key, access_token)
        
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
        ConfigManager.save_config(gemini_key, access_token)
        print(f"\nGenerared new Access Key: {access_token}\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
