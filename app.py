from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'senyum'
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
        
    except mysql.connector.Error as err:
        print(f"Error fetching data: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return context

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    api_key = data.get('apiKey')
    message = data.get('message')
    history = data.get('history', [])
    
    if not api_key:
        return jsonify({'error': 'API Key is required'}), 400
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Fetch context from DB
    context = get_chat_context()
    if not context:
        return jsonify({'error': 'Failed to fetch system context'}), 500

    # Format Context Strings
    faq_context = "\n\n".join([f"Q: {item['pertanyaan']}\nA: {item['jawaban']}" for item in context['faq']])
    
    fasilitas_List = []
    for f in context['fasilitas']:
        telp = f['telp'] if f['telp'] else ''
        fasilitas_str = f"{f['nama_fasilitas']}|{f['alamat']}|{f['kelurahan']}|{f['kecamatan']}"
        if telp:
            fasilitas_str += f"|{telp}"
        fasilitas_List.append(fasilitas_str)
        
    fasilitas_context = "\n".join(fasilitas_List)

    # Build System Instruction (Same as before)
    system_instruction = f"""Anda adalah asisten customer service virtual untuk Website Kota Pangkal Pinang. 
Tugas Anda adalah membantu pengunjung dengan ramah, sopan, dan profesional.

DATA YANG TERSEDIA:

=== FREQUENTLY ASKED QUESTIONS (FAQ) ===
{faq_context}

=== FASILITAS DI PANGKAL PINANG ===
Format: Nama|Alamat|Kelurahan|Kecamatan|Telp
Total: {len(context['fasilitas'])} fasilitas (SEMUA DATA)

{fasilitas_context}

PEDOMAN MENJAWAB:
1. Gunakan nada yang RAMAH, SOPAN, dan HANGAT
2. Jika pertanyaan ada di FAQ atau data fasilitas, berikan jawaban lengkap dan informatif
3. Jika diminta informasi fasilitas tertentu (masjid, gereja, sekolah, rumah sakit, dll), cari di data fasilitas
4. Jika pertanyaan di luar data yang tersedia, jawab dengan sopan: 
   "Maaf, saya belum memiliki informasi tersebut. Silakan hubungi kantor pelayanan Kota Pangkal Pinang untuk informasi lebih lanjut."
5. Selalu akhiri jawaban dengan ramah
6. Gunakan Bahasa Indonesia yang baik dan benar

Ingat: Anda adalah perwakilan resmi Kota Pangkal Pinang, selalu profesional dan membantu!"""

    try:
        # Initialize Client
        client = genai.Client(api_key=api_key)
        
        # Prepare content hierarchy
        # New SDK uses specific types or dictionaries for messages
        # Structure: contents=[Content(role='user', parts=[Part.from_text('...')])] or simple dicts
        
        chat_history = []
        for msg in history:
            role = 'user' if msg['role'] == 'user' else 'model'
            chat_history.append(types.Content(
                role=role,
                parts=[types.Part(text=msg['text'])]
            ))
            
        # Add the new message to history logically for the request (or let chat sessions handle it)
        # Using generate_content is stateless, useful for manual history management
        # But here we want a chat/content generation.
        
        # Append current user message
        chat_history.append(types.Content(
            role='user',
            parts=[types.Part(text=message)]
        ))

        # Generate content
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1000
            )
        )
        
        return jsonify({'text': response.text})
        
    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
