from config import bot,dp,COOKIES
from aiogram import types
from helper import is_valid,prepare_urls,send_video,normalize_url
import requests
import re
import os

@dp.inline_handler()
async def inline_echo(inline_query):
	user = inline_query.from_user
	video_url = inline_query.query.replace("\\","").split("/")
	if is_valid(video_url):
		await bot.send_message(user.id,'Sending...')
		url = await normalize_url(video_url)
		text = requests.get(url,cookies=COOKIES).text

		response = re.findall('"url":"([^"]+)"',text)

		vid_urls = prepare_urls(response)

		input_content = types.InputTextMessageContent(inline_query.query)
		username = re.findall('"full_name":"([^"]+)"', text)
		display_url = re.findall('"url":"([^"]+)"', text)

		pic_url = prepare_urls(display_url)

		username = re.findall('"username":"([^"]+)"', text)

		item = types.InlineQueryResultVideo(id='1', title=f'{username[1]}',video_url=f'{video_url}',
											mime_type='video/mp4',thumb_url=f'{pic_url[0]}',caption='it is caption',description=f'@igviddwdbot',
											  input_message_content=input_content)
		await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)

		vid_ct = requests.get(f"{vid_urls[0]}")

		if os.path.exists(os.path.join(os.getcwd(),"videos")):
			pass
		else:
			os.makedirs("videos")

		with open(f'videos/{user.id}.mp4','wb') as f:
			f.write(vid_ct.content)
		await send_video(user,username=None)
	else:
		await bot.send_message(user.id,'Invalid URL.')