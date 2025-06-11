import os

from aiogram import Bot, Dispatcher
import asyncio

from services.database import init_tables

TOKEN = os.getenv("TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    await init_tables()
    
    from handlers import start, add_record, add_report, admin_panel
    
    dp.include_router(start.router)
    dp.include_router(add_record.router)
    dp.include_router(add_report.router)
    dp.include_router(admin_panel.router)
    
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())