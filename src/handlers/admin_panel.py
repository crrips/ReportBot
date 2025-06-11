import os

from aiogram.types.input_file import FSInputFile
from aiogram import Router, types, F

from services.keyboards import admin_panel_keyboard
from utils.records_to_xlsx import records_to_xlsx
from utils.reports_to_xlsx import reports_to_xlsx
from services.auth_admin import auth_admin
from services.database import conn_db

router = Router()

@router.message(F.text == "Адмін панель")
async def admin_panel(message: types.Message):
    user_id = message.from_user.id

    if not auth_admin(user_id):
        return

    await message.answer("Вітаємо в адмін панелі! Тут ви можете отримати статистику по користувачам та записам.", reply_markup=admin_panel_keyboard())
    
@router.callback_query(F.data == "admin_records_stats")
async def admin_records_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if not auth_admin(user_id):
        return
    
    conn = await conn_db()
    query = '''
        SELECT u.name, r.*
        FROM users u
        LEFT JOIN records r ON u.telegram_id = r.user_id
        ORDER BY u.name;
    '''
    records = await conn.fetch(query)
    await conn.close()
    
    file_path = records_to_xlsx(records)
    document = FSInputFile(file_path)
    
    await callback.message.answer_document(document)

    await callback.answer("Статистика записів відправлена.")
    
    os.remove(file_path)
    
@router.callback_query(F.data == "admin_reports_stats")
async def admin_reports_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if not auth_admin(user_id):
        return
    
    conn = await conn_db()
    query = '''
        SELECT u.name, r.*
        FROM users u
        LEFT JOIN reports r ON u.telegram_id = r.user_id
        ORDER BY u.name;
    '''
    reports = await conn.fetch(query)
    await conn.close()
    
    file_path = reports_to_xlsx(reports)
    document = FSInputFile(file_path)
    
    await callback.message.answer_document(document)

    await callback.answer("Статистика звітів відправлена.")
    
    os.remove(file_path)    
