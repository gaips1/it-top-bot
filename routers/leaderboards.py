from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command

from middlewares import GetUserMiddleware
from database.models.users import User

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

@router.callback_query(F.data.startswith("leaderboard/"))
async def leaderboard(callback: CallbackQuery, user: User, state: FSMContext):
    try:
        leaderboard_type = callback.data.split('/')[-1]
    except (IndexError, ValueError):
        await callback.answer("Ошибка: Неверный формат callback-данных.")
        return

    is_group_leaderboard = leaderboard_type == "group"

    leaderboard_data = await user.get_leaderboard(callback.from_user.id, state, is_group=is_group_leaderboard)
    header = "<b>🏆 Таблица лидеров 🏆</b>\n\n"

    leaderboard_entries = [
        f"{entry.position}. {entry.full_name} - {entry.amount} топмани"
        for entry in leaderboard_data.root[:12 if is_group_leaderboard else 10]
    ]
    text = header + "\n".join(leaderboard_entries)

    if is_group_leaderboard:
        button_text = "Таблица лидеров (в потоке)"
        button_callback = f"leaderboard/stream"
    else:
        button_text = "Таблица лидеров (в группе)"
        button_callback = f"leaderboard/group"

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=button_text, callback_data=button_callback),
            ],
            [
                InlineKeyboardButton(text="Главное Меню", callback_data="mm")
            ]
        ]
    )
    
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=reply_markup)