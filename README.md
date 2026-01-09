# Optimized Chatbot for Pangkal Pinang

Chatbot yang dioptimalkan untuk memberikan respon yang efisien berdasarkan tipe pertanyaan.

## Fitur Optimasi

1. **Respon Berdasarkan Tipe Pertanyaan**:
   - **Lokasi** (contoh: "di mana alamat..."): Hanya menampilkan alamat dan koordinat
   - **Jam Operasional** (contoh: "jam buka..."): Format ringkas "Jam Buka: [waktu]"
   - **Prosedur/Syarat** (contoh: "cara membuat..."): Daftar bernomor yang ringkas
   - **Pertanyaan Umum** (apa/siapa/mengapa): 1-2 kalimat langsung ke inti
   - **Default**: Maksimal 3 kalimat

2. **Penghematan Token**:
   - Batas token disesuaikan otomatis
   - Respon lebih ringkas tapi tetap informatif
   - Format yang konsisten

## Cara Menguji

1. Pastikan server berjalan:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Jalankan skrip pengujian:
   ```bash
   python test_responses.py
   ```

3. Tekan Enter untuk melihat contoh respon dari berbagai tipe pertanyaan

## Contoh Pertanyaan untuk Dicoba

- "Di mana letak kantor kelurahan?"
- "Jam buka kantor kecamatan?"
- "Apa saja syarat bikin KTP?"
- "Bagaimana cara mengurus surat pindah?"
- "Apa itu KIP?"

## Catatan

- Pastikan untuk mengatur `API_KEY` di `test_responses.py` dengan token akses yang valid
- Server harus berjalan di `http://localhost:8000` (default)
- Untuk produksi, pastikan untuk mengamankan API key dan menggunakan HTTPS
