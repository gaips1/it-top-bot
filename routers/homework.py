from collections import defaultdict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command

from utils.middlewares import GetUserMiddleware
from database.models.users import User
from api.models.homework import Homework
from utils import split_text

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

@router.callback_query(F.data.startswith("homework/"))
async def homework_handler(callback: CallbackQuery, user: User, state: FSMContext):
    try:
        type = int(callback.data.split('/')[-1])
    except (IndexError, ValueError):
        return

    homeworks = await user.get_homeworks(state, type)
    if not homeworks:
        return
    
    homeworks_by_spec = defaultdict(list)
    for hw in homeworks:
        homeworks_by_spec[hw.name_spec].append(hw)

    text_parts = []
    for spec, hws in homeworks_by_spec.items():
        text_parts.append(f"📚 <b>{spec}</b>")
        for hw in hws:
            hw: Homework

            text_parts.append(f"  📌 <b>Тема:</b> {hw.theme}")
            text_parts.append(f"  👨‍🏫 <b>Преподаватель:</b> {hw.fio_teach}")
            text_parts.append(f"  📅 <b>Выдано:</b> {hw.creation_time.strftime('%d.%m.%Y')}")
            text_parts.append(f"  📅 <b>Срок:</b> {hw.completion_time.strftime('%d.%m.%Y')}\n")

            text_parts.append(f"  ℹ️ <b>Комментарий: {hw.comment or "нет"}</b>")
            text_parts.append(f"  📩 <a href='{hw.file_path}'>Скачать назначенное дз</a>")
            
            if hw.homework_stud:
                text_parts.append(f"\n  📅 <b>Сдано:</b> {hw.homework_stud.creation_time.strftime('%d.%m.%Y')}")
                if hw.homework_stud.stud_answer is not None:
                    text_parts.append(f"  ✅ <b>Твой ответ:</b> {hw.homework_stud.stud_answer}")
                if hw.homework_stud.mark is not None:
                    text_parts.append(f"  ⭐ <b>Оценка:</b> {hw.homework_stud.mark}")
                if hw.homework_stud.file_path is not None:
                    text_parts.append(f"  📩 <a href='{hw.homework_stud.file_path}'>Скачать выполненное дз</a>")
            else:
                text_parts.append(f"  📩 <b>Загрузить выполненное дз - /homework</b>")

            if hw.homework_comment and hw.homework_comment.text_comment:
                comment = hw.homework_comment.text_comment
                text_parts.append(f"  💬 <b>Комментарий преподавателя:</b> {comment}")

            text_parts.append("\n")

    text = "Домашние задания (последние 6)\n\n" + "\n".join(text_parts)

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"Текущие дз {"(Вы здесь)" if type == 3 else ""}" , callback_data="homework/3"),
            ],
            [
                InlineKeyboardButton(text=f"На проверке {"(Вы здесь)" if type == 2 else ""}", callback_data="homework/2"),
            ],
            [
                InlineKeyboardButton(text=f"Проверено {"(Вы здесь)" if type == 1 else ""}", callback_data="homework/1"),
            ],
            [
                InlineKeyboardButton(text="Главное Меню", callback_data="mm")
            ]
        ]
    )
    
    await callback.answer()

    if len(text) > 4096:
        text_parts = split_text(text)
        await callback.message.edit_text(text_parts[0], link_preview_options={"is_disabled":True})
        
        for part in text_parts[1:-1]:
            await callback.message.answer(part, link_preview_options={"is_disabled":True})

        await callback.message.answer(text_parts[-1], reply_markup=reply_markup, link_preview_options={"is_disabled":True})
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup, link_preview_options={"is_disabled":True})

@router.message(Command("homework"))
async def do_homework_handler(message: Message, user: User, state: FSMContext):
    return await message.answer("Будет доступно позже.")