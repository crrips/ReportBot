from services.database import conn_db

async def report_summary(user_id: int, today: str) -> str:
    """
    Generate a summary report for the user on a given day.
    """
    conn = await conn_db()
    
    query_plan = '''
        SELECT ads, responses, records
        FROM reports
        WHERE user_id = $1 AND is_plan = TRUE AND DATE(created_at) = $2
    '''
    plan = await conn.fetchrow(query_plan, user_id, today)
    
    query_report = '''
        SELECT ads, responses, records
        FROM reports
        WHERE user_id = $1 AND is_report = TRUE AND DATE(created_at) = $2
    '''
    report = await conn.fetchrow(query_report, user_id, today)
    await conn.close()
    
    ads_plan = int(plan['ads']) if plan else 0
    responses_plan = int(plan['responses']) if plan else 0
    records_plan = int(plan['records']) if plan else 0
    
    ads_report = int(report['ads']) if report else 0
    responses_report = int(report['responses']) if report else 0
    records_report = int(report['records']) if report else 0
    
    today = today.strftime("%d.%m.%Y")
    
    summary = (
        f"📅 Звіт за {today}\n\n"
        f"План:\n"
        f"Оголошень: {ads_plan}\n"
        f"Відповідей: {responses_plan}\n"
        f"Записів: {records_plan}\n\n"
        f"Звіт:\n"
        f"Оголошень: {ads_report}\n"
        f"Відповідей: {responses_report}\n"
        f"Записів: {records_report}\n\n"
    )
    
    if ads_report >= ads_plan and responses_report >= responses_plan and records_report >= records_plan:
        summary += "✅ Молодець! Ти виконав план!"
    else:
        summary += "❗ Є розбіжності!"
    return summary.strip()
