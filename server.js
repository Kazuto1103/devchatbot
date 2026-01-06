import express from 'express';
import mysql from 'mysql2/promise';
import cors from 'cors';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Create a connection pool
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'senyum',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// API endpoint to get chat context for AI
app.get('/api/chat-context', async (req, res) => {
    try {
        // Fetch FAQ data
        const [faqRows] = await pool.query('SELECT pertanyaan, jawaban FROM faq');

        // Fetch fasilitas data
        const [fasilitasRows] = await pool.query(`
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
        `);

        res.json({
            faq: faqRows,
            fasilitas: fasilitasRows
        });
    } catch (error) {
        console.error('Database query error:', error);
        res.status(500).json({ error: 'Failed to fetch chat context' });
    }
});

app.get('/api/places', async (req, res) => {
    try {
        // Fetch all facilities from the fasilitas table
        const [rows] = await pool.query(`
            SELECT 
                id,
                nama_fasilitas as nama,
                alamat as lokasi,
                kelurahan,
                kecamatan,
                latitude,
                longitude,
                telp,
                email,
                website
            FROM fasilitas
            ORDER BY nama_fasilitas
        `);

        res.json(rows);
    } catch (error) {
        console.error('Database query error:', error);
        res.status(500).json({ error: 'Failed to fetch data' });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
