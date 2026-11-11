"""Telegram-бот (Could, SVL-24). Тонкий адаптер aiogram 3 над app/services.

Запуск: pip install -r requirements-bot.txt; SVL_BOT_TOKEN=... python -m bot.bot
"""

import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from app.bootstrap import init_database
from app.clock import now_local
from bot.texts import HELP, address_text, parse_address, status_text

UserAddresses = dict[int, tuple[str, str]]


async def start(message: Message) -> None:
    await message.answer(HELP)


async def set_address(
    message: Message,
    command: CommandObject,
    session_factory: sessionmaker,
    user_addresses: UserAddresses,
) -> None:
    parsed = parse_address(command.args or "")
    if parsed is None:
        await message.answer("Формат: /address Шевченка 10")
        return
    user_addresses[message.from_user.id] = parsed
    with session_factory() as session:
        await message.answer(address_text(session, *parsed))


async def get_status(
    message: Message, session_factory: sessionmaker, user_addresses: UserAddresses
) -> None:
    address = user_addresses.get(message.from_user.id)
    if address is None:
        await message.answer("Спершу вкажіть адресу: /address Шевченка 10")
        return
    with session_factory() as session:
        await message.answer(status_text(session, *address, now_local()))


def create_dispatcher(session_factory: sessionmaker) -> Dispatcher:
    """Залежності передаються хендлерам через workflow_data aiogram, а не глобальні змінні."""
    router = Router()
    router.message.register(start, CommandStart())
    router.message.register(set_address, Command("address"))
    router.message.register(get_status, Command("status"))
    dp = Dispatcher(session_factory=session_factory, user_addresses={})
    dp.include_router(router)
    return dp


async def main() -> None:  # pragma: no cover — потребує токена Telegram
    engine, session_factory = init_database()
    try:
        await create_dispatcher(session_factory).start_polling(Bot(os.environ["SVL_BOT_TOKEN"]))
    finally:
        engine.dispose()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
