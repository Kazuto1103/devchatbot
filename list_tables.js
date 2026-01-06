import mysql from 'mysql2/promise';

async function listTables() {
    try {
        const connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: '',
            database: 'senyum'
        });

        console.log('Connected to senyum!');
        const [rows] = await connection.query('SHOW TABLES');
        console.log('Tables available:');
        rows.forEach(row => {
            console.log(`- ${Object.values(row)[0]}`);
        });
        await connection.end();
    } catch (error) {
        console.error('Error:', error);
    }
}

listTables();
