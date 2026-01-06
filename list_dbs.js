import mysql from 'mysql2/promise';

async function listDatabases() {
    try {
        const connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: ''
        });

        console.log('Connected to MySQL!');
        const [rows] = await connection.query('SHOW DATABASES');
        console.log('Databases available:');
        rows.forEach(row => {
            console.log(`- ${row.Database}`);
        });
        await connection.end();
    } catch (error) {
        console.error('Error:', error);
    }
}

listDatabases();
