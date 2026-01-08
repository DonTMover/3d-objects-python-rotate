import asyncio
import logging
import sys
from os import getenv
import time
import aiohttp

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command(commands=["shape"]))
async def shape_handler(message: Message) -> None:
    """Usage: /shape <shape> [size]

    Examples:
    /shape sphere 1.5
    /shape cube 2
    /shape cone 1
    /shape cylinder 0.8
    Можно использовать русские названия: "сфера", "куб", "конус", "цилиндр".
    """
    from . import renderer
    text = message.text or ""
    parts = text.split()
    raw_shape = parts[1] if len(parts) > 1 else "sphere"
    size = 1.0
    if len(parts) > 2:
        try:
            size = float(parts[2])
        except ValueError:
            pass

    # mapping Russian names to internal English identifiers
    mapping = {
        "сфера": "sphere",
        "шар": "sphere",
        "куб": "cube",
        "конус": "cone",
        "цилиндр": "cylinder",
        "цилиндры": "cylinder",
        "сфера": "sphere",
        "конус": "cone",
    }

    shape = mapping.get(raw_shape.lower(), raw_shape.lower())

    # Instead of server-side rendering, open the Web App viewer with parameters
    from os import getenv
    webapp_url = getenv("WEBAPP_URL", "http://localhost:8000/")
    # ensure trailing slash
    if not webapp_url.endswith("/"):
        webapp_url += "/"
    url = f"{webapp_url}?shape={shape}&size={size}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"Open {shape} (size={size})", web_app=WebAppInfo(url=url))
    ]])
    await message.answer(f"Open interactive viewer for {shape}:", reply_markup=kb)


@dp.message(Command(commands=["webapp"]))
async def webapp_handler(message: Message) -> None:
    """Send a button that opens the interactive web app (Three.js)"""
    # WEBAPP_URL can be set to a public HTTPS endpoint (ngrok or deployed service)
    from os import getenv
    webapp_url = getenv("WEBAPP_URL", "http://localhost:8000/")
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Open 3D Viewer", web_app=WebAppInfo(url=webapp_url))
    ]])
    await message.answer("Open interactive viewer:", reply_markup=kb)


@dp.message(Command(commands=["help"]))
async def help_handler(message: Message) -> None:
    text = (
        "Использование:\n"
        "/shape <фигура> [размер]\n\n"
        "Поддерживаемые фигуры:\n"
        "  - сфера, шар (sphere)\n"
        "  - куб (cube)\n"
        "  - конус (cone)\n"
        "  - цилиндр (cylinder)\n\n"
        "Примеры:\n"
        "  /shape сфера 1.5\n"
        "  /shape cube 2\n"
    )
    await message.answer(text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # start background heartbeat task to notify webapp about bot health
    async def heartbeat_loop():
        webapp = getenv("WEBAPP_URL", "http://localhost:8000/")
        if not webapp.endswith("/"):
            webapp += "/"
        url = webapp.rstrip('/') + "/heartbeat"
        async with aiohttp.ClientSession() as session:
            # send initial start ping
            payload = {"ts": time.time(), "bot_start": time.time()}
            try:
                await session.post(url, json=payload)
            except Exception:
                pass
            while True:
                try:
                    await session.post(url, json={"ts": time.time()})
                except Exception:
                    pass
                await asyncio.sleep(30)

    asyncio.create_task(heartbeat_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())