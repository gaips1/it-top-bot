from collections import defaultdict
from datetime import timedelta
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from middlewares import GetUserMiddleware
from database.models.users import User

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

def split_text(text: str, limit: int = 4096) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    remaining_text = text

    while remaining_text:
        if len(remaining_text) <= limit:
            parts.append(remaining_text)
            break

        chunk = remaining_text[:limit]
        
        last_newline = chunk.rfind('\n')
        last_space = chunk.rfind(' ')

        split_pos = max(last_newline, last_space)

        if split_pos == -1:
            split_pos = limit
        
        parts.append(remaining_text[:split_pos])
        
        remaining_text = remaining_text[split_pos:].lstrip()

    return parts

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
            text_parts.append(f"  📌 <b>Тема:</b> {hw.theme}")
            text_parts.append(f"  👨‍🏫 <b>Преподаватель:</b> {hw.fio_teach}")
            text_parts.append(f"  📅 <b>Выдано:</b> {hw.creation_time.strftime('%d.%m.%Y')}")
            text_parts.append(f"  📅 <b>Срок:</b> {hw.completion_time.strftime('%d.%m.%Y')}")
            
            if hw.homework_stud:
                text_parts.append(f"  📅 <b>Сдано:</b> {hw.homework_stud.creation_time.strftime('%d.%m.%Y')}")
                if hw.homework_stud.stud_answer is not None:
                    text_parts.append(f"  ✅ <b>Твой ответ:</b> {hw.homework_stud.stud_answer}")
                if hw.homework_stud.mark is not None:
                    text_parts.append(f"  ⭐ <b>Оценка:</b> {hw.homework_stud.mark}")
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
        await callback.message.edit_text(text_parts[0])
        
        for part in text_parts[1:-1]:
            await callback.message.answer(part)

        await callback.message.answer(text_parts[-1], reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup)