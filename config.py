import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types
from settings import BOT_TOKEN
import os

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)