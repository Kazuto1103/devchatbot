# Panduan Testing Response Chatbot

Dokumen ini menjelaskan cara melakukan testing terhadap respon chatbot dan format yang diharapkan.

## Struktur Testing

### 1. File Test
- `test_responses.py`: Berisi skrip untuk menguji berbagai tipe pertanyaan
- `TEST_RESPONSE_GUIDE.md`: Panduan ini

### 2. Format Response yang Diharapkan

#### a. Pertanyaan Lokasi
```
[NAMA TEMPAT]
Alamat: [alamat lengkap]
Kecamatan: [nama kecamatan]
Koordinat: [jika tersedia]
Telp: [jika tersedia]
```

#### b. Jam Operasional
```
[NAMA TEMPAT]
Jam Operasional: [hari] [waktu buka] - [waktu tutup] WIB
Contoh: Senin-Jumat 08.00-16.00 WIB
```

#### c. Persyaratan Dokumen
```
1. [Persyaratan 1]
   - Keterangan tambahan
2. [Persyaratan 2]
   - Keterangan tambahan
```

### 3. Menjalankan Test

```bash
# Pastikan server berjalan
cd backend
uvicorn main:app --reload --port 5000

# Di terminal terpisah, jalankan test
cd ..
python test_responses.py
```

### 4. Daftar Pertanyaan Test

1. **Lokasi**
   - Di mana alamat Diskominfo pangkal pinang?
   - Di mana kantor kelurahan?

2. **Jam Operasional**
   - Jam buka kantor kelurahan?
   - Jam kerja pemkot pangkal pinang?

3. **Persyaratan**
   - Apa saja syarat membuat KTP?
   - Bagaimana cara mengurus surat nikah?

4. **Informasi Umum**
   - Apa itu Kartu Indonesia Pintar?
   - Bagaimana cara daftar BPJS Kesehatan?

### 5. Kriteria Sukses

- Respon tidak boleh kosong
- Format sesuai dengan tipe pertanyaan
- Informasi yang diberikan akurat
- Respon tidak terpotong (harus diakhiri dengan tanda baca yang sesuai)

### 6. Troubleshooting

- Jika mendapatkan timeout, pastikan server berjalan dengan baik
- Jika respon tidak sesuai format, periksa log server untuk pesan error
- Pastikan koneksi internet stabil untuk akses ke API Gemini
