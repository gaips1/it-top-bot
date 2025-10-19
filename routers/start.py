from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command

from middlewares import GetUserMiddleware
from database.models.users import User

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

inline_keyboard=[
    [
        InlineKeyboardButton(text="Домашние задания (WIP)", callback_data="homework/")
    ],
    [
        InlineKeyboardButton(text="Посещаемость/оценки", callback_data="activity/0")
    ],
    [
        InlineKeyboardButton(text="Таблица лидеров", callback_data="leaderboard/stream")
    ],
    [
        InlineKeyboardButton(text="Ваши награды", callback_data="rewards/0")
    ]
]

async def mm(event: Message | CallbackQuery, user: User, state: FSMContext):
    profile = await user.get_user_info(event.from_user.id, state)

    text = (
        f"Привет, {profile.full_name}!\n"
        f"Ваш ID: {profile.student_id}\n"
        f"Дата регистрации: {profile.registration_date}\n"
        f"Ваша группа: {profile.group_name}\n\n"
        f"Кол-во топкоинов: {profile.gaming_points[0].points}\n"
        f"Кол-во топгемов: {profile.gaming_points[1].points}\n"
        f"Кол-во топмани (сумма): {profile.gaming_points[0].points + profile.gaming_points[1].points}\n"
    )

    if isinstance(event, Message):
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
    else:
        await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
        await event.answer()

@router.message(Command("start"))
async def start_handler(message: Message, user: User, state: FSMContext):
    return await mm(message, user, state)

@router.callback_query(F.data.startswith("mm"))
async def mm_handler(callback: CallbackQuery, user: User, state: FSMContext):
    return await mm(callback, user, state)