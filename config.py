import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv('BOT_TOKEN')

#USER_AGENT = "Instagram 117.0.0.28.123 Android (28/9.0; 420dpi; 1080x1920; OnePlus; ONEPLUS A3003; OnePlus3; qcom; en_US; 180322800)"

USER_AGENT = "Mozilla/5.0 (Linux; Android 7.1.2; SM-G935T Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/51.0.2704.81 Mobile Safari/537.36 Instagram 241.1.1.0.1.18.114 Android (23/6.0.1; 560dpi; 1440x2560; samsung; SM-G935T; hero2qltetmo; qcom; en_US"

HEADERS = {"User-Agent": USER_AGENT}

COOKIES = {'sessionid': os.getenv('SESSIONID')}
PASSWORD = os.getenv("PASSWORD")

bot = Bot(BOT_TOKEN)

storage = MemoryStorage()

dp = Dispatcher(bot,storage=storage)
