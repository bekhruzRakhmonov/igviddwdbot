import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types
from settings import BOT_TOKEN
import os
# from dotenv import load_dotenv
# load_dotenv()

logging.basicConfig(level=logging.INFO)

# BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
