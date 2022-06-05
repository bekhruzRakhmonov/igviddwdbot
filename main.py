from config import bot,dp,COOKIES
from aiogram import executor, types
from aiogram.utils.executor import start_webhook
import db_helper as db
from helper import is_valid,prepare_urls,send_video,normalize_url
import requests
from requests.sessions import Session
from threading import Thread,local
import re
import os
import sys


@dp.message_handler(commands=['users'])
async def send_users_count(message: types.Message):
    if int(message.from_user.id) == int(os.getenv("ADMIN_ID")):
        users = db.get_users_count()

        await bot.send_message(message.from_user.id,users)
    else:
        await bot.send_message(message.from_user.id,"Invalid URL.")

thread_local = local()
def get_session() -> Session:
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session

def download_link(url:str):
    session = requests.Session()
    with session.get(url) as response:
        return response.iter_content(chunk_size=1024*1024),sys.getsizeof(response.content),response.content

async def get_vid_url(vid_urls):
    for vid_url in vid_urls:
        if ".mp4" in  vid_url:
            return vid_url

async def download_video(user_id,gen_content,size,content):
    size_mb = round(size/(1024*1024),2)
    if size_mb >= 50:
        ctx = b""
        c = 0
        while True:
            ctx += next(gen_content)
            c += 1
            if c == 49:
                break

        with open(f'videos/{user_id}.mp4','wb') as f:
            f.write(ctx)
    else:
        with open(f'videos/{user_id}.mp4','wb') as f:
            f.write(content)

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id 
    user = db.get_user(user_id)
    if len(user) == 0:
        db.add_user(user_id)
    await bot.send_message(message.from_user.id,'Send me URL.')

@dp.message_handler(content_types=['text'])
async def get_url(message: types.Message):
    user_id = message.from_user.id 
    user = db.get_user(user_id)
    if len(user) == 0:
        db.add_user(user_id)

    if is_valid(message.text):
        await bot.send_message(user_id,'Sending...')
        url = await normalize_url(message.text)
        text =  requests.get(url,cookies=COOKIES).text

        response = re.findall('"url":"([^"]+)"',text)

        vid_urls = await prepare_urls(response)

        vid_url = await get_vid_url(vid_urls)

        gen_content,size,content = download_link(vid_url)

        if os.path.exists(os.path.join(os.getcwd(),"videos")):
            pass
        else:
            os.makedirs("videos")
        await download_video(user_id,gen_content,size,content)
        await send_video(user_id)
        
    else:
        await bot.send_message(user_id,'Invalid URL.')

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
