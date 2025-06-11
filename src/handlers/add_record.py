from datetime import datetime

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F

from services.keyboards import confirm_record
from services.database import conn_db

class AddRecordForm(StatesGroup):
    student = State()
    subject = State()
    link = State()
    phone_number = State()
    lesson_date = State()
    lesson_time = State()
    
router = Router()

@router.message(F.text == "Заповнити запис")
async def start(message: types.Message, state: FSMContext):
    await message.answer("Введи ім'я учня")
    await state.set_state(AddRecordForm.student)

@router.message(AddRecordForm.student)
async def get_student(message: types.Message, state: FSMContext):
    student = message.text
    if student == None or student.strip() == "":
        await message.answer("Ім'я учня не може бути порожнім. Спробуй ще раз.")
        return
    await state.update_data(student=student)
    await message.answer("Тепер введи назву предмета")
    await state.set_state(AddRecordForm.subject)

@router.message(AddRecordForm.subject)
async def get_subject(message: types.Message, state: FSMContext):
    subject = message.text
    if subject == None or subject.strip() == "":
        await message.answer("Назва предмета не може бути порожньою. Спробуй ще раз.")
        return
    await state.update_data(subject=subject)
    await message.answer("Введи посилання на зустріч")
    await state.set_state(AddRecordForm.link)
    
@router.message(AddRecordForm.link)
async def get_link(message: types.Message, state: FSMContext):
    link = message.text
    if link == None or link.strip() == "":
        await message.answer("Посилання не може бути порожнім. Спробуй ще раз.")
        return
    await state.update_data(link=link)
    await message.answer("Введи номер телефону")
    await state.set_state(AddRecordForm.phone_number)
    
@router.message(AddRecordForm.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text
    if phone_number == None or phone_number.strip() == "":
        await message.answer("Номер телефону не може бути порожнім. Спробуй ще раз.")
        return
    await state.update_data(phone_number=phone_number)
    await message.answer("Введи дату заняття (у форматі ДД.ММ.РРРР)")
    await state.set_state(AddRecordForm.lesson_date)
    
@router.message(AddRecordForm.lesson_date)
async def get_lesson_date(message: types.Message, state: FSMContext):
    lesson_date_str = message.text
    try:
        lesson_date = datetime.strptime(lesson_date_str, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Невірний формат дати. Спробуй ще раз.")
        return
    
    await state.update_data(lesson_date=lesson_date)
    await message.answer("Введи час заняття (у форматі ГГ:ХХ)")
    await state.set_state(AddRecordForm.lesson_time)
    
@router.message(AddRecordForm.lesson_time)
async def get_lesson_time(message: types.Message, state: FSMContext):
    lesson_time_str = message.text
    try:
        lesson_time = datetime.strptime(lesson_time_str, "%H:%M").time()
    except ValueError:
        await message.answer("Невірний формат часу. Спробуй ще раз.")
        return
    
    await state.update_data(lesson_time=lesson_time)
    data = await state.get_data()

    student = data.get("student")
    subject = data.get("subject")
    link = data.get("link")
    phone_number = data.get("phone_number")
    lesson_date = data.get("lesson_date").strftime("%d.%m.%Y")
    lesson_time = data.get("lesson_time").strftime("%H:%M")
    
    confirmation_text = (
        f"Учень: {student}\n"
        f"Предмет: {subject}\n"
        f"Посилання: {link}\n"
        f"Телефон: {phone_number}\n"
        f"Дата заняття: {lesson_date}\n"
        f"Час заняття: {lesson_time}"
    )
    await message.answer(confirmation_text)
    await message.answer("Всі дані записано вірно?", reply_markup=confirm_record())
    
@router.callback_query(F.data == "record_confirm_yes")
async def save_record(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    user_id = callback.from_user.id
    student = data.get("student")
    subject = data.get("subject")
    link = data.get("link")
    phone_number = data.get("phone_number")
    lesson_date = data.get("lesson_date")
    lesson_time = data.get("lesson_time")
    
    conn = await conn_db()
    query = '''
        INSERT INTO records (user_id, student, subject, link, phone_number, lesson_date, lesson_time, created_at)
        VALUES (
            $1, $2, $3, $4, $5, $6, $7,
            TIMEZONE('Europe/Kyiv', NOW())
            )
    '''
    await conn.execute(query, user_id, student, subject, link, phone_number, lesson_date, lesson_time)
    await conn.close()
    
    await callback.message.answer("✅ Запис успішно додано!")
    await state.clear()
    
@router.callback_query(F.data == "record_confirm_no")
async def cancel_record(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Заповнення запису скасовано.")
    await state.clear()
