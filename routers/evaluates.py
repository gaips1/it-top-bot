from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.models.users import User
from aiogram.types import Message
from aiogram import Router, F

from utils.middlewares import GetUserMiddleware

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

async def check_for_evaluates(message: Message, user: User, state: FSMContext):
    evaluates = await user.get_lesson_evaluations(state)
    
    if not evaluates:
        return
    
    evl = evaluates[0]

    text = f"Оцените занятие: {evl.spec_name.upper()} {evl.date_visit.strftime('%d.%m.%Y')}\nОцените работу преподавателя {evl.fio_teach}:"
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐", callback_data=f"evaluates/{evl.key}/1"),
                InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"evaluates/{evl.key}/3")
            ],
            [
                InlineKeyboardButton(text="⭐⭐", callback_data=f"evaluates/{evl.key}/2"),
                InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"evaluates/{evl.key}/4"),
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"evaluates/{evl.key}/5"),
            ],
        ]
    )

    return await message.reply(text=text, reply_markup=reply_markup)

@router.callback_query(F.data.startswith("evaluates/"))
async def evaluates_handler(callback: CallbackQuery, user: User, state: FSMContext):
    data = callback.data.split('/')
    
    key = data[1]
    teach_mark = int(data[2])

    await callback.answer()

    if len(data) <= 3:
        text = "Спасибо за оценку работы преподавателя!\nТеперь оцените качество урока:"
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⭐", callback_data=f"evaluates/{key}/{teach_mark}/1"),
                    InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"evaluates/{key}/{teach_mark}/3")
                ],
                [
                    InlineKeyboardButton(text="⭐⭐", callback_data=f"evaluates/{key}/{teach_mark}/2"),
                    InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"evaluates/{key}/{teach_mark}/4"),
                ],
                [
                    InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"evaluates/{key}/{teach_mark}/5"),
                ],
            ]
        )
        return await callback.message.edit_text(text=text, reply_markup=reply_markup)
    else:
        lesson_mark = int(data[3])
        await callback.message.edit_text(text="Спасибо за ваши оценки!")
        await user.evaluate_lesson(key=key, mark_teach=teach_mark, mark_lesson=lesson_mark)
        return await check_for_evaluates(callback.message, user, state)