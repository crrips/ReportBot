from services.database import conn_db

async def check_plan(user_id: int, today: str) -> bool:
    """
    Check that plan consists of one report for the user on a given day.
    """
    conn = await conn_db()
    query = """
        SELECT COUNT(*) FROM reports
        WHERE user_id = $1 AND is_plan = TRUE AND DATE(created_at) = $2
    """
    count = await conn.fetchval(query, user_id, today)
    await conn.close()
    
    return count == 1

async def check_report(user_id: int, today: str) -> bool:
    """
    Check that report consists of one report for the user on a given day.
    """
    conn = await conn_db()
    query = """
        SELECT COUNT(*) FROM reports
        WHERE user_id = $1 AND is_report = TRUE AND DATE(created_at) = $2
    """
    count = await conn.fetchval(query, user_id, today)
    await conn.close()
    
    return count == 1
