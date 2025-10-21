from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

import database.models.users as users
from routers.auth import auth_handler

class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = await users.get_user_by_id(event.from_user.id)

        if not user:
            return await auth_handler(event.from_user.id, data["state"])

        data['user'] = user
        return await handler(event, data)