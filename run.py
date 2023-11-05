from aiogram.types import BotCommand

from handlers.messages import messages_router 
from core.config import bot, dp

import asyncio

dp.include_router(messages_router)


async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            BotCommand(
                command='start', 
                description='Перезапуск бота'
                )
        ]
    )


async def start(dispatcher) -> None:
    bot_name = dict(await bot.get_me()).get('username')
    await set_default_commands(dispatcher)
    print(f'#    start on @{bot_name}')


async def end(dispatcher) -> None:
    bot_name = dict(await bot.get_me()).get('username')
    print(f'#    end on @{bot_name}')


async def main():
    await start(dispatcher=dp)
    await dp.start_polling(bot)
    await end(dispatcher=dp)
    

if __name__ == "__main__":
    asyncio.run(main())