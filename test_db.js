const mysql = require('mysql2/promise');

async function testQuery() {
    try {
        const connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: '',
            database: 'senyum'
        });

        console.log('Connected to senyum database!');

        // Test FAQ query
        const [faqRows] = await connection.query('SELECT pertanyaan, jawaban FROM faq');
        console.log('\n=== FAQ Results ===');
        console.log(`Found ${faqRows.length} FAQ entries`);

        // Test fasilitas query - search for Masjid
        const [masjidRows] = await connection.query(`
            SELECT nama_fasilitas, alamat, kelurahan, kecamatan 
            FROM fasilitas 
            WHERE nama_fasilitas LIKE '%Masjid%' 
            LIMIT 10
        `);
        console.log('\n=== Masjid Results ===');
        console.log(`Found ${masjidRows.length} masjid entries`);
        masjidRows.forEach(m => {
            console.log(`- ${m.nama_fasilitas}`);
        });

        // Search specifically for "Masjid Jamik"
        const [jamikRows] = await connection.query(`
            SELECT nama_fasilitas, alamat, kelurahan, kecamatan 
            FROM fasilitas 
            WHERE nama_fasilitas LIKE '%Jamik%'
        `);
        console.log('\n=== Masjid Jamik Search ===');
        console.log(`Found ${jamikRows.length} results for "Jamik"`);
        jamikRows.forEach(m => {
            console.log(`- ${m.nama_fasilitas} at ${m.alamat}`);
        });

        await connection.end();
    } catch (error) {
        console.error('Error:', error);
    }
}

testQuery();
