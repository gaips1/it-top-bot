from collections import defaultdict
from datetime import timedelta
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F

from utils.middlewares import GetUserMiddleware
from utils import split_text
from database.models.users import User

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())

@router.callback_query(F.data.startswith("activity/"))
async def activity_handler(callback: CallbackQuery, user: User, state: FSMContext):
    try:
        i = int(callback.data.split('/')[-1])
    except (IndexError, ValueError):
        return

    activities = await user.get_activities(state)
    if not activities:
        return
    
    latest_activity_date = activities[0].date_visit

    start_of_first_week = latest_activity_date - timedelta(days=latest_activity_date.weekday())
    start_of_first_week = start_of_first_week.replace(hour=0, minute=0, second=0, microsecond=0)

    start_of_target_week = start_of_first_week - timedelta(weeks=i) 
    end_of_target_week = start_of_target_week + timedelta(days=5)

    activities_by_date = defaultdict(list)
    for ac in activities:
        if start_of_target_week <= ac.date_visit < end_of_target_week:
            activities_by_date[ac.date_visit].append(ac)

    header = f"<b>🗓️ Учебная неделя {start_of_target_week.strftime('%d.%m.%Y')} - {end_of_target_week.strftime('%d.%m.%Y')}</b>\n"

    daily_entries = []
    for date in sorted(activities_by_date.keys()):
        day_header = f"\n<b><u>{date.strftime('%d.%m.%Y')}</u></b>"
        daily_entries.append(day_header)

        for ac in reversed(activities_by_date[date]):
            marks_str = ", ".join(map(str, ac.all_marks)) if ac.all_marks else "нет"
            entry = (
                f"🎓 <b>{ac.spec_name}</b>\n"
                f"    - <b>Пара:</b> {ac.lesson_number}\n"
                f"    - <b>Статус:</b> {ac.status_was_translated}\n"
                f"    - <b>Преподаватель:</b> {ac.teacher_name}\n"
                f"    - <b>Тема:</b> {ac.lesson_theme}\n"
                f"    - <b>Оценки:</b> {marks_str}\n"
            )
            daily_entries.append(entry)

    if daily_entries:
        text = header + "\n".join(daily_entries)
    else:
        text = header + "\nЗанятий на этой неделе не было."

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Вперед", callback_data="activity/" + str(i+1)),
            ],
            [
                InlineKeyboardButton(text="Главное Меню", callback_data="mm")
            ]
        ]
    )
    if i > 0:
        reply_markup.inline_keyboard[0].insert(0, InlineKeyboardButton(text="Назад", callback_data="activity/" + str(i-1)))
    
    await callback.answer()

    if len(text) > 4096:
        text_parts = split_text(text)
        await callback.message.edit_text(text_parts[0])
        
        for part in text_parts[1:-1]:
            await callback.message.answer(part)

        await callback.message.answer(text_parts[-1], reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup)