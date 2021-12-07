import aiogram
import logging
from aiogram import Bot, Dispatcher, executor, types

from aiogram.utils.executor import start_webhook
from settings import (BOT_TOKEN,HEROKU_APP_NAME,WEBHOOK_URL, WEBHOOK_PATH,WEBAPP_HOST, WEBAPP_PORT)

import requests as r
import re
import os
import sqlite3

conn = sqlite3.connect('db.db')
cursor = conn.cursor()

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


async def on_startup(dp):
	logging.warning(
		'Starting connection. ')
	await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)

def is_valid(url):
	req = r.get(f'{url}')
	if (re.match(r"https://www.instagram.com/tv/",url) or re.match(r"https://www.instagram.com/p/",url)) and req.status_code == 200:
		return True
	else:
		return False

@dp.message_handler(commands=['hechkimbilmidi'])
async def send_users_count(message: types.Message):
	users_count = cursor.execute("SELECT id FROM users")
	for user in users_count:
		await bot.send_message(message.from_user.id,user)
@dp.message_handler(commands=['start'])
async def start_message(message): 
	user = cursor.execute("SELECT * FROM users WHERE user_id='{}'".format(message.from_user.id)).fetchone()
	if user == None:
		cursor.execute("INSERT INTO users(user_id) VALUES ({})".format(message.from_user.id))
		conn.commit()
	await bot.send_message(message.from_user.id,'Send me URL.')
async def send_video(user,viewers,username,description):
	await bot.send_video(user.id,open(f'videos/{user.id}.mp4','rb'),caption=f"<b>Username</b>: {username[0]}\n<b>Viewers count</b>: {viewers[0]}\n@igviddwd_bot",parse_mode='HTML')
	if os.path.exists(f"videos/{user.id}.mp4"):
		os.remove(f"videos/{user.id}.mp4")
def prepare_urls(matches):
	return list({match.replace("\\u0026", "&") for match in matches})
@dp.message_handler(content_types=['text'])
async def get_url(message):
	user = message.from_user
	print(message.text)
	if is_valid(message.text):
		await bot.send_message(user.id,'Sending...')
		text =  r.get(f"{message.text}")
		response = re.findall('"video_url":"([^"]+)"',text.text)
		username = re.findall('"full_name":"([^"]+)"', text.text)
		description = re.findall('"text":"([^"]+)"', text.text)
		viewers = re.findall('"video_view_count":([^"]+)',text.text)
		vid_urls = prepare_urls(response)
		print(vid_urls)
		data = r.get(f"{vid_urls[0]}")
		with open(f'videos/{message.from_user.id}.mp4','wb') as f:
			f.write(data.content)
		await send_video(user,viewers,username,description)
	else:
		await bot.send_message(user.id,'Invalid url.')

@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
	user = inline_query.from_user
	video_url = inline_query.query.replace("\\","")
	if is_valid(video_url):
		await bot.send_message(user.id,'Sending...')
		text = r.get(f"{inline_query.query}").text
		response = re.findall('"video_url":"([^"]+)"',text)
		viewers = re.findall('"video_view_count":([^"]+)',text)
		vid_urls = prepare_urls(response)
		input_content = types.InputTextMessageContent(inline_query.query)
		username = re.findall('"full_name":"([^"]+)"', text)
		display_url = re.findall('"display_url":"([^"]+)"', text)
		pic_url = prepare_urls(display_url)
		description = re.findall('"text":"([^"]+)"', text)
		modified_description = description[2].replace("\\n","")
		print(description)
		item = types.InlineQueryResultVideo(id='1', title=f'{username[0]}',video_url=f'{video_url}',
											mime_type='video/mp4',thumb_url=f'{pic_url[0]}',caption='it is caption',description=f'{modified_description[:30]}...\nKo\'rishlar soni:{viewers[0]}',
											  input_message_content=input_content)
		await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)
		data = r.get(f"{vid_urls[0]}")
		with open(f'videos/{user.id}.mp4','wb') as f:
			f.write(data.content)
		await send_video(user,viewers,username,description)
	else:
		await bot.send_message(user.id,'Invalid URL.')


if __name__ == '__main__':
	start_webhook(
		dispatcher=dp,
		webhook_path=WEBHOOK_PATH,
		skip_updates=True,
		on_startup=on_startup,
		host=WEBAPP_HOST,
		port=WEBAPP_PORT,
	)