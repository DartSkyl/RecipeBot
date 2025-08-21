import asyncio

from aiogram.types import BotCommand

import handlers  # noqa
from loader import dp, bot, db_connect
from utils.routers import admin_router, users_router


async def start_up():
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(users_router)
    await db_connect()
    await bot.set_my_commands([
        BotCommand(command='start', description='Главное меню и рестарт')
    ])
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
