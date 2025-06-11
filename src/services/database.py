import os

import asyncpg

DB_CONFIG = {
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

SCHEMA_NAME = os.getenv('DB_SCHEMA', 'public')

async def conn_db():
    return await asyncpg.connect(
        **DB_CONFIG,
        server_settings={
            'search_path': SCHEMA_NAME
        })

async def init_user_table():
    conn = await conn_db()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username VARCHAR(100) NOT NULL,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    await conn.close()
    
async def init_record_table():
    conn = await conn_db()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            student VARCHAR(100) NOT NULL,
            subject VARCHAR(50) NOT NULL,
            link TEXT NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            lesson_date DATE NOT NULL,
            lesson_time TIME NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    await conn.close()
    
async def init_report_table():
    conn = await conn_db()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            ads INTEGER NOT NULL,
            responses INTEGER NOT NULL,
            records INTEGER NOT NULL,
            is_plan BOOLEAN NOT NULL DEFAULT FALSE,
            is_report BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    await conn.close()
    
async def init_tables():
    await init_user_table()
    await init_record_table()
    await init_report_table()