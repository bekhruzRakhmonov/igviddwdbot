from config import bot,dp,COOKIES
from aiogram import executor, types
from aiogram.utils.executor import start_webhook
from db_helper import DBHelper
from inline_handler import inline_echo
from helper import is_valid,prepare_urls,send_video,normalize_url
import requests
import re
import os


@dp.message_handler(commands=['secretuserscount'])
async def send_users_count(message: types.Message):
	db = DBHelper(message.from_user.id)
	users_count = db.get_users_count()
	for user in users_count:
		await bot.send_message(message.from_user.id,user)

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message): 
	db = DBHelper(message.from_user.id) 
	db.create_db()
	user = db.check_user()
	if user == None:
		db.add_user()
		db.commit()
	await bot.send_message(message.from_user.id,'Send me URL.')

@dp.message_handler(content_types=['text'])
async def get_url(message: types.Message):
	user = message.from_user
	if is_valid(message.text):
		await bot.send_message(user.id,'Sending...')
		url = await normalize_url(message.text)
		text =  requests.get(url,cookies=COOKIES).text

		response = re.findall('"url":"([^"]+)"',text)
		username = re.findall('"full_name":"([^"]+)"', text)
		description = re.findall('"text":"([^"]+)"', text)
		viewers = re.findall('"video_view_count":([^"]+)',text)

		vid_urls = prepare_urls(response)

		vid_ct = requests.get(f"{vid_urls[0]}")

		if os.path.exists(os.path.join(os.getcwd(),"videos")):
			pass
		else:
			os.makedirs("videos")

		with open(f'videos/{message.from_user.id}.mp4','wb') as f:
			f.write(vid_ct.content)
		await send_video(user,viewers,username,description)
	else:
		await bot.send_message(user.id,'Invalid URL.')

if __name__ == '__main__':
	executor.start_polling(dp,skip_updates=True)
