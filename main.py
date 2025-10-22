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

from routers import *
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

    await message.answer(f"Удалил {del_id} из бд")

async def main():
    await init_db()

    bot.cached_me = await bot.get_me()

    dp.include_routers(
        start_router,
        auth_router,
        ld_router,
        rewards_router,
        activity_router,
        homework_router,
        evaluates_router
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())