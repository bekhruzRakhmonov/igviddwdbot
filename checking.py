from config import bot,dp
import requests as r
import re
import os
import cgitb
from urllib.parse import urlparse

# show detailed errors
cgitb.enable()

def is_valid(url):
	if re.match(r"https://www.instagram.com/tv/",url) or re.match(r"https://www.instagram.com/p/",url) or re.match(r"https://www.instagram.com/reel/",url) :
		req = r.get(url)
		if req.status_code == 200:
			return True
	else:
		return False
def prepare_urls(matches):
	return list({match.replace("\\u0026", "&") for match in matches})

async def send_video(user,viewers,username,description):
	print(viewers)
	viewers_count = viewers[0].strip(',')
	await bot.send_video(user.id,open(f'videos/{user.id}.mp4','rb'),caption=f"<b>Viewers count</b>: <i>{viewers_count}</i>\n@igviddwdbot",parse_mode='HTML')
	# if os.path.exists(f"videos/{user.id}.mp4"):
		# os.remove(f"videos/{user.id}.mp4")