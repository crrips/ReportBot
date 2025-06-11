from services.database import conn_db

async def count_records(user_id: int, today: str) -> int:
    """
    Count the number of records for a user on a given day.
    """
    conn = await conn_db()
    query = """
        SELECT COUNT(*) FROM records
        WHERE user_id = $1 AND DATE(created_at) = $2
    """
    count = await conn.fetchval(query, user_id, today)
    await conn.close()
    
    return count if count is not None else 0
