import asyncio
import os
from dotenv import load_dotenv
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

import routers
from database.db import init_db
import database.models.users as users

load_dotenv()
TOKEN = os.environ.get("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

@dp.message(Command("delete"))
async def delete_handler(message: Message, command: CommandObject):
    if message.from_user.id != 1014268792:
        return
    
    del_id = command.args.split(" ")[0]
    await users.delete_user(int(del_id))

    return await message.answer(f"Удалил {del_id} из бд")

async def main():
    await init_db()

    dp.include_routers(
        routers.start_router,
        routers.auth_router,
        routers.ld_router,
        routers.rewards_router,
        routers.activity_router,
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())