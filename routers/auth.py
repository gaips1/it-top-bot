import asyncio
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.filters import Command

from api.scraper import TopAcademyScraper as tap
import database.models.users as users

router = Router()

class LoginForm(StatesGroup):
    text = State()

async def auth_handler(id: int, state: FSMContext, first_time = True, invalid = False):
    await state.set_state(LoginForm.text)

    from main import bot
    if invalid:
        return await bot.send_message(id, "Неверный логин или пароль. Пожалуйста, введите действующие данные.\n\nВведите ваш логин и пароль в формате: `логин пароль`.")
    elif first_time:
        return await bot.send_message(id, "Пожалуйста, введите ваш логин и пароль от Top Academy в формате: `логин пароль`. Для отмены введите `отмена`.")
    
    await bot.send_message(id, "Добро пожаловать! Пожалуйста, введите ваш логин и пароль от Top Academy в формате: `логин пароль`. Для отмены введите `отмена`.")

@router.message(LoginForm.text)
async def login(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        return await message.answer("Авторизация отменена.")
    
    try:
        username, password = message.text.split()
    except ValueError:
        return await message.answer("Пожалуйста, введите логин и пароль в правильном формате: `логин пароль`.\nПопробуйте еще раз:")
    
    usr = tap(username, password)
    async with usr as scraper:
        logged_in = await scraper._login()

    if not logged_in:
        return await message.answer("Не удалось войти. Пожалуйста, проверьте ваш логин и пароль и попробуйте снова:")

    await state.clear()
    user = await users.create_user(id=message.from_user.id, username=username, password=password, access_token=usr.access_token)

    await message.answer("Спасибо! Ваши данные сохранены. Вы можете изменить их в любой момент, используя команду /relogin.\n\nПереношу Вас в главное меню...")
    await asyncio.sleep(1.5)

    from routers.start import start_handler
    return await start_handler(message, user, state)

@router.message(Command("relogin"))
async def relogin_handler(message: Message, state: FSMContext):
    user = await users.get_user_by_id(message.from_user.id)
    if not user:
        return await auth_handler(message, state)
    
    return await auth_handler(message, state, first_time=False)