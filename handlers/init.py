from aiogram.bot import Bot
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
import config

logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="w")

bot = Bot(token=config.API_KEY)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
