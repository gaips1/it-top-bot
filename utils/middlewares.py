import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

import database.models.users as users
from routers.auth import auth_handler

class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = await users.get_user_by_id(event.from_user.id)

        if not user:
            return await auth_handler(event.from_user.id, data["state"], data="юзер не найден. ")
        
        data['user'] = user
        
        current_time = time.time()
        if user.id not in users.evaluate_check_cooldown or current_time - users.evaluate_check_cooldown[user.id] > 300:
            if isinstance(event, CallbackQuery) and event.data.startswith("evaluates/"): return await handler(event, data)
            users.evaluate_check_cooldown[user.id] = current_time
            from routers.evaluates import check_for_evaluates
            await check_for_evaluates(event.message if isinstance(event, CallbackQuery) else event, user, data["state"])

        data['user'] = user
        return await handler(event, data)