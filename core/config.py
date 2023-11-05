from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from dotenv import dotenv_values

import logging

config = dotenv_values(".env")


API_KEY = config.get("TELEGRAM_API_KEY")
START_MESSAGE_STICKER_ID = config.get("START_MESSAGE_STICKER_ID")


bot = Bot(token=API_KEY)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="w")
