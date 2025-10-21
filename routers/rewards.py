from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from utils.middlewares import GetUserMiddleware
from database.models.users import User

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

@router.callback_query(F.data.startswith("rewards/"))
async def rewards_handler(callback: CallbackQuery, user: User, state: FSMContext):
    try:
        i = int(callback.data.split('/')[-1])
    except (IndexError, ValueError):
        return

    rewards = await user.get_rewards(callback.from_user.id, state)
    if not rewards:
        return
    
    start_index = i * 10
    end_index = (i + 1) * 10

    rewards = rewards.root[start_index:end_index]

    header = "<b>🏆 Ваши награды 🏆</b>\n\n"
    rewards_entries = [
        f"{reward.date.strftime('%d.%m.%Y %H:%M')}\n{reward.achievements_name_translated}: +{reward.current_point} {reward.point_types_name_translated}\n----------------------------"
        for reward in rewards
    ]
    text = header + "\n".join(rewards_entries)

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Вперед", callback_data="rewards/" + str(i+1)),
            ],
            [
                InlineKeyboardButton(text="Главное Меню", callback_data="mm")
            ]
        ]
    )
    if i > 0:
        reply_markup.inline_keyboard[0].insert(0, InlineKeyboardButton(text="Назад", callback_data="rewards/" + str(i-1)))
    
    await callback.answer()
    await callback.message.edit_text(text, reply_markup=reply_markup)