from config import bot,dp
from aiogram import types
from helper import is_valid,prepare_urls,send_video
import requests
import re

@dp.inline_handler()
async def inline_echo(inline_query):
	user = inline_query.from_user
	video_url = inline_query.query.replace("\\","")
	if is_valid(video_url):
		await bot.send_message(user.id,'Sending...')

		text = requests.get(f"{inline_query.query}").text

		response = re.findall('"video_url":"([^"]+)"',text)
		viewers = re.findall('"video_view_count":([^"]+)',text)

		vid_urls = prepare_urls(response)

		input_content = types.InputTextMessageContent(inline_query.query)
		username = re.findall('"full_name":"([^"]+)"', text)
		display_url = re.findall('"display_url":"([^"]+)"', text)

		pic_url = prepare_urls(display_url)

		description = re.findall('"text":"([^"]+)"', text)

		item = types.InlineQueryResultVideo(id='1', title=f'{username[0]}',video_url=f'{video_url}',
											mime_type='video/mp4',thumb_url=f'{pic_url[0]}',caption='it is caption',description=f'Ko\'rishlar soni:{viewers[0]}',
											  input_message_content=input_content)
		await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)

		vid_ct = requests.get(f"{vid_urls[0]}")

		with open(f'videos/{user.id}.mp4','wb') as f:
			f.write(vid_ct.content)
		await send_video(user,viewers,username,description)
	else:
		await bot.send_message(user.id,'Invalid URL.')