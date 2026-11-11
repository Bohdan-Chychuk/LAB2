"""Telegram-бот (Could, SVL-24). Тонкий адаптер aiogram 3 над app/services.

Запуск: pip install -r requirements-bot.txt; SVL_BOT_TOKEN=... python -m bot.bot
"""

import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

from app.clock import now_local
from app.db import Base, database_url, make_engine, make_session_factory
from app.seed import seed_addresses, seed_schedule
from bot.texts import HELP, address_text, parse_address, status_text

engine = make_engine(database_url())
Base.metadata.create_all(engine)
SessionLocal = make_session_factory(engine)
user_addresses: dict[int, tuple[str, str]] = {}

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(HELP)


@dp.message(Command("address"))
async def set_address(message: Message, command: CommandObject) -> None:
    parsed = parse_address(command.args or "")
    if parsed is None:
        await message.answer("Формат: /address Шевченка 10")
        return
    user_addresses[message.from_user.id] = parsed
    with SessionLocal() as session:
        await message.answer(address_text(session, *parsed))


@dp.message(Command("status"))
async def get_status(message: Message) -> None:
    address = user_addresses.get(message.from_user.id)
    if address is None:
        await message.answer("Спершу вкажіть адресу: /address Шевченка 10")
        return
    with SessionLocal() as session:
        await message.answer(status_text(session, *address, now_local()))


async def main() -> None:
    with SessionLocal() as session:
        seed_addresses(session)
        seed_schedule(session)
    await dp.start_polling(Bot(os.environ["SVL_BOT_TOKEN"]))


if __name__ == "__main__":
    asyncio.run(main())
