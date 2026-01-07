# Panduan Penggunaan DevChatbot API

Dokumen ini menjelaskan cara instalasi, konfigurasi, dan menjalankan server API DevChatbot.

## 1. Persiapan (Prerequisites)

Sebelum memulai, pastikan sistem Anda memiliki:

- **Python 3.8** atau lebih baru.
- **MySQL Server** (XAMPP/WAMP/Laragon) untuk database.
- Database bernama `social` (atau sesuaikan di kode) yang telah diimpor dengan file `senyum.sql`.

## 2. Instalasi

1. Buka terminal atau Command Prompt.
2. Arahkan ke direktori `backend` proyek ini:
   ```bash
   cd backend
   ```
3. Instal semua pustaka Python yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```

## 3. Konfigurasi Database

Pastikan file `senyum.sql` telah diimpor ke database MySQL Anda.
Secara default, aplikasi akan mencari database dengan konfigurasi:

- Host: `localhost`
- User: `root`
- Password: `` (kosong)
- Database: `social`

Jika konfigurasi MySQL Anda berbeda, Anda dapat menyesuaikannya dengan membuat file `.env` (atau mengedit yang sudah ada) di folder `backend`, atau mengedit variabel `db_config` di `main.py`.

## 4. Menjalankan Server

Untuk menjalankan server API, gunakan perintah berikut di terminal (di dalam folder `backend`):

```bash
python main.py
```

### Setup Wizard (Pertama Kali)

Jika ini pertama kalinya Anda menjalankan aplikasi dan belum ada file konfigurasi (`server_config.json`), aplikasi akan menjalankan mode setup interaktif di terminal:

1. **Masukkan Gemini API Key**: Paste API Key Gemini Anda dari Google AI Studio.
2. **Access Key Generator**: Sistem akan otomatis membuat `Chatbot Access Key` unik.
3. **Simpan Key**: Salin dan simpan `Chatbot Access Key` yang ditampilkan. Key ini akan digunakan oleh aplikasi Frontend untuk berkomunikasi dengan API ini.

File `server_config.json` akan dibuat otomatis untuk menyimpan kredensial ini.

## 5. Mengakses API

Setelah server berjalan, Anda akan melihat pesan seperti:
`Uvicorn running on http://0.0.0.0:5000`

### Dokumentasi Interaktif (Swagger UI)

Buka browser dan akses URL berikut untuk melihat dan mencoba API secara langsung:
👉 **[http://localhost:5000/docs](http://localhost:5000/docs)**

### Endpoint Utama

Lihat file `API_DOCUMENTATION.md` untuk detail teknis lengkap.

- **Status Check**: `GET /api/status`
- **Chat**: `POST /api/chat` atau `GET /api/chat` (untuk testing cepat)

## 6. Troubleshooting

- **Error: Module not found**: Pastikan Anda sudah menjalankan `pip install -r requirements.txt`.
- **Error Connecting to Database**: Periksa apakah MySQL sudah berjalan (misal via XAMPP Control Panel) dan nama database sesuai.
- **Port Already in Use**: Jika port 5000 sedang digunakan aplikasi lain, Anda bisa mengubah port pada baris terakhir file `main.py`.

---

Happy Coding! 🚀
