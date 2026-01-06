import mysql from 'mysql2/promise';

async function describeTables() {
    try {
        const connection = await mysql.createConnection({
            host: 'localhost',
            user: 'root',
            password: '',
            database: 'senyum_test'
        });

        console.log('--- Table: gereja ---');
        const [gerejaRows] = await connection.query('DESCRIBE gereja');
        console.log(JSON.stringify(gerejaRows, null, 2));

        console.log('\n--- Table: mesjid ---');
        const [mesjidRows] = await connection.query('DESCRIBE mesjid');
        console.log(JSON.stringify(mesjidRows, null, 2));

        await connection.end();
    } catch (error) {
        console.error('Error:', error);
    }
}

describeTables();
