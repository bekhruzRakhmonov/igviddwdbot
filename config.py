import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types
# from settings import BOT_TOKEN
import os
# from dotenv import load_dotenv
# load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv('BOT_TOKEN')
COOKIES = {'sessionid': os.getenv('SESSIONID')}
# HEADERS = {'User-Agent':'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)'}


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
