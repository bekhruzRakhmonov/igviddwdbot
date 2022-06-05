import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv('BOT_TOKEN')
COOKIES = {'sessionid': os.getenv('SESSIONID')}
PASSWORD = os.getenv("PASSWORD")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
