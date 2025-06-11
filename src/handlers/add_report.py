from datetime import datetime

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
import pytz

from utils.check_amount import check_plan, check_report
from utils.report_summary import report_summary
from utils.record_counter import count_records
from services.keyboards import confirm_report
from services.database import conn_db

class AddReportForm(StatesGroup):
    plan = State()
    plan_records = State()
    report_ads = State()
    report_responses = State()
    confirm = State()
    
router = Router()

async def add_plan(message: types.Message, state: FSMContext, is_plan: bool = True):
    await state.set_state(AddReportForm.plan)
    if is_plan:
        await message.answer("Це план на день. Введи кількість записів, які ти плануєш зробити.")
        await state.update_data(is_plan=True)
        await state.set_state(AddReportForm.plan_records)
        
@router.message(AddReportForm.plan_records)        
async def add_plan_records(message: types.Message, state: FSMContext):
    try:
        records = int(message.text)
        if records < 1:
            await message.answer("Будь ласка, введи число більше 0.")
            return
        ads = records * 80
        responses = records * 2
        await state.update_data(records=records)
        await state.update_data(ads=ads, responses=responses)
        await message.answer(f"Кількість оголошень: {ads}\n"
                             f"Кількість відповідей: {responses}\n"
                             f"Кількість записів: {records}")
        await message.answer("Підтверджуєш ці дані?", reply_markup=confirm_report())
        await state.set_state(AddReportForm.confirm)
    except ValueError:
        await message.answer("Будь ласка, введи коректне число.")
        return

async def add_report(message: types.Message, state: FSMContext, is_report: bool = True):
    await state.set_state(AddReportForm.report_ads)
    if is_report:
        await message.answer("Це звіт за день. Введи кількість оголошень, які ти розмістив.")
        await state.update_data(is_report=True)

@router.message(AddReportForm.report_ads)
async def add_report_ads(message: types.Message, state: FSMContext):
    try:
        ads = int(message.text)
        if ads < 0:
            await message.answer("Будь ласка, введи число більше або рівне 0.")
            return
        await state.update_data(ads=ads)
        
        await message.answer("Тепер введи кількість відповідей")
        await state.set_state(AddReportForm.report_responses)
        
    except ValueError:
        await message.answer("Будь ласка, введи коректне число.")
        return
        
@router.message(AddReportForm.report_responses)
async def add_report_responses(message: types.Message, state: FSMContext):
    try:
        responses = int(message.text)
        if responses < 0:
            await message.answer("Будь ласка, введи число більше або рівне 0.")
            return
        await state.update_data(responses=responses)
        
        data = await state.get_data()
        ads = data.get('ads')
        today = datetime.now(pytz.timezone('Europe/Kyiv')).date()
        records = await count_records(message.from_user.id, today)
        await state.update_data(records=records)
        await message.answer(f"Кількість оголошень: {ads}\n"
                                f"Кількість відповідей: {responses}\n"
                                f"Кількість записів: {records}")
        await message.answer("Підтверджуєш ці дані?", reply_markup=confirm_report())
        await state.set_state(AddReportForm.confirm)
            
    except ValueError:
        await message.answer("Будь ласка, введи коректне число.")
            
@router.callback_query(F.data == "report_confirm_yes")
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    user_id = callback.from_user.id
    ads = data.get('ads')
    responses = data.get('responses')
    records = data.get('records')
    is_plan = data.get('is_plan', False)
    is_report = data.get('is_report', False)
    
    conn = await conn_db()
    query = """
    INSERT INTO reports (user_id, ads, responses, records, is_plan, is_report, created_at)
    VALUES (
        $1, $2, $3, $4, $5, $6,
        TIMEZONE('Europe/Kyiv', NOW())
    )
    """
    await conn.execute(query, user_id, ads, responses, records, is_plan, is_report)
    await conn.close()
    
    if is_plan:
        await callback.message.answer("✅ План на день збережено.")
    else:
        await callback.message.answer("✅ Звіт за день збережено.")
        await callback.message.answer(await report_summary(user_id, datetime.now(pytz.timezone('Europe/Kyiv')).date()))

    await state.clear()
    
@router.callback_query(F.data == "report_confirm_no")
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Дані не збережено.")
    await state.clear()

@router.message(F.text == "Створити план/звіт")
async def create_report(message: types.Message, state: FSMContext):
    tz = pytz.timezone('Europe/Kyiv')
    cur_time = datetime.now(tz).strftime("%H:%M")
    
    is_plan_exists = await check_plan(message.from_user.id, datetime.now(tz).date())
    
    if cur_time >= "00:00" and cur_time < "15:00":
        # plan
        if is_plan_exists:
            await message.answer("План на день вже заповнено. Можна заповнити звіт з 18:00.")
            return
        await add_plan(message, state)
        return
    elif cur_time >= "15:00" and cur_time < "18:00":
        # deadline
        if is_plan_exists:
            await message.answer("План на день вже заповнено. Можна заповнити звіт з 18:00.")
            return
        else:
            await message.answer("Ти чомусь не заповнив план на день :/")
            return
    elif cur_time >= "18:00" and cur_time <= "23:59":
        # report
        if not is_plan_exists:
            await message.answer("План на день не було заповнено :/")
            return
        if await check_report(message.from_user.id, datetime.now(tz).date()):
            await message.answer("Звіт на сьогодні вже заповнено.")
            await message.answer(await report_summary(message.from_user.id, datetime.now(tz).date()))
            return
        await add_report(message, state)
        return