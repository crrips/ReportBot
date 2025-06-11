from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from services.auth_admin import auth_admin

def main_menu(user_id: int):
    keyboard_rows = [
            [
                KeyboardButton(text="Заповнити запис")
            ],
            [
                KeyboardButton(text="Створити план/звіт")
            ]
    ]
    
    if auth_admin(user_id):
        keyboard_rows.append([KeyboardButton(text="Адмін панель")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True
    )

def confirm_record():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Так", callback_data="record_confirm_yes")
            ],
            [
                InlineKeyboardButton(text="Ні", callback_data="record_confirm_no")
            ]
        ]
    )
    
def confirm_report():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Так", callback_data="report_confirm_yes")
            ],
            [
                InlineKeyboardButton(text="Ні", callback_data="report_confirm_no")
            ]
        ]
    )
    
def admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Статистика записів", callback_data="admin_records_stats")
            ],
            [
                InlineKeyboardButton(text="Статистика звітів", callback_data="admin_reports_stats")
            ],
        ]
    )
