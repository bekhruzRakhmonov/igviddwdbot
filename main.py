from config import bot,dp,COOKIES,HEADERS
import aiogram
from aiogram import executor, types
from aiogram.utils import exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
import db_helper as db
from helper import is_valid,prepare_urls,normalize_url
import requests
import asyncio
from requests.sessions import Session
from threading import Thread,local
import re
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

ADMIN_ID = int(os.getenv("ADMIN_ID"))

class Form(StatesGroup):
    message = State()
    username = State()

@dp.message_handler(commands=['broadcast'])
async def handle_broadcast(message: types.Message):
    if int(message.from_user.id) == ADMIN_ID:
        await Form.message.set()
        await message.reply("Send me your message")
    else:
        await bot.send_message(message.from_user.id,"Invalid URL")

@dp.message_handler(commands=['cancel'],state=Form.username)
async def cancel_state(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id,"Send me video, photo(s) or stories link.")

@dp.message_handler(commands=['download_profile_photo'])
async def download_photo(message: types.Message):
    await Form.username.set()
    await message.reply("Send me username of account you want to download profile photo.\nExample: <b>cristiano</b> without any symbols or prefixs",parse_mode="HTML")
    await message.answer("To cancel /cancel")

@dp.message_handler(state=Form.username)
async def download_profile_photo(message: types.Message, state: FSMContext):

    session = get_session()

    try:
        text = session.get(f"https://www.instagram.com/{message.text}/",cookies=COOKIES,headers=HEADERS).text

        user_ids = re.findall(r'"profile_id":"([^"]+)"',text)
        
        url = f"https://i.instagram.com/api/v1/users/{user_ids[0]}/info"
        response = session.get(url,cookies=COOKIES,headers=HEADERS)

        status = response.json()["status"]

        if not status == "ok":
            return await message.answer("Photo not found")

        user = response.json()["user"]

        hd_profile_pic = user.get("hd_profile_pic_versions")

        if hd_profile_pic is not None:
            if len(hd_profile_pic) > 1:
                profile_pic_url = hd_profile_pic[1]["url"]
            else:
                profile_pic_url = hd_profile_pic[0]["url"]
        else:
            profile_pic_url = user.get("profile_pic_url")

        await bot.send_message(message.from_user.id,'Profile photo is uploading...')
        await bot.send_chat_action(message.from_user.id, 'upload_photo')
        await bot.send_photo(message.from_user.id,profile_pic_url,caption="<i>@igviddwdbot</i>",parse_mode='HTML')
        

    except Exception as e:
        await message.answer("I encountered errors while uploading photo.")
        log.info(e)

    await message.answer('To cancel /cancel')

@dp.message_handler(commands=['users'])
async def send_users_count(message: types.Message):
    if int(message.from_user.id) == ADMIN_ID:
        users = len(db.get_users())

        await bot.send_message(message.from_user.id,users)
    else:
        await bot.send_message(message.from_user.id,"Invalid URL.")

thread_local = local()
def get_session() -> Session:
    if not hasattr(thread_local,'session'):
        thread_local.session = requests.Session()
    return thread_local.session

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id 
    user = db.get_user(user_id)
    if len(user) == 0:
        db.add_user(user_id)
    await bot.send_message(message.from_user.id,'Send me video, photo(s) or stories link.')

async def send_video(user_id,url):
    await bot.send_message(user_id,'Video is uploading...')
    await bot.send_chat_action(user_id, 'upload_video')
    await bot.send_video(user_id,url,caption="<i>@igviddwdbot</i>",parse_mode='HTML')

async def send_photo(user_id,url):
    await bot.send_message(user_id,'Photo is uploading...')
    await bot.send_chat_action(user_id, 'upload_photo')
    await bot.send_photo(user_id,url,caption="<i>@igviddwdbot</i>",parse_mode='HTML')

async def send_photos(user_id,carousel_media):
    media = []
    count = 0
    for img in carousel_media:
        count += 1
        url = img["image_versions2"]["candidates"][0]["url"]
        media.append(types.InputMediaPhoto(url,caption="<i>@igviddwdbot</i>",parse_mode='HTML'))
        if count == 10:
            break

    await bot.send_message(user_id,'Photo is uploading...')
    await bot.send_chat_action(user_id, 'upload_photo')
    await bot.send_media_group(user_id,media=media)

async def download_highlights_and_stories(is_story=False,is_highlight=False,user_id:str = None,media_id: str = None,tg_user_id: str = None,highlight_id: str = None):
    session = get_session()
    if is_story and not is_highlight:
        response = session.get(f"https://i.instagram.com/api/v1/feed/user/{user_id}/reel_media/",cookies=COOKIES,headers=HEADERS)
        items = response.json()["items"]
        for item in items:
            if item["pk"] == int(media_id):
                if item["media_type"] == 2:
                    video_versions = item["video_versions"]
                    return await send_video(tg_user_id,video_versions[0]["url"])
                if item["media_type"] == 1:
                    image_versions2 = item["image_versions2"]["candidates"]
                    return await send_photo(tg_user_id,image_versions2[0]["url"])

    elif not is_story and is_highlight:
        response = session.get(f"https://i.instagram.com/api/v1/feed/reels_media/?user_ids={highlight_id}",cookies=COOKIES,headers=HEADERS)
        items = response.json()["reels"][highlight_id]["items"]
        for item in items:
            if int(item["pk"]) == int(media_id):
                if item["media_type"] == 2:
                    video_versions = item["video_versions"]
                    return await send_video(tg_user_id,video_versions[0]["url"])
                if item["media_type"] == 1:
                    image_versions2 = item["image_versions2"]["candidates"]
                    return await send_photo(tg_user_id,image_versions2[0]["url"])
    return None 

@dp.message_handler(content_types=['text'])
async def get_url(message: types.Message):
    user_id = message.from_user.id 
    user = db.get_user(user_id)
    if len(user) == 0:
        db.add_user(user_id)

    if is_valid(message.text):

        session = get_session()

        is_story,is_highlight,media_id,fixed_url = await normalize_url(message.text)

        try:           
            if not is_story:
                response = session.get(fixed_url,cookies=COOKIES,headers=HEADERS)
                media_id = response.json()["items"][0]["pk"]

                response = session.get(f"https://i.instagram.com/api/v1/media/{media_id}/info/",cookies=COOKIES,headers=HEADERS)
            else:
                if is_highlight:
                    response = session.get(f"https://i.instagram.com/api/v1/media/{media_id[0]}/info/",headers=HEADERS,cookies=COOKIES)
                else:
                    response = session.get(f"https://i.instagram.com/api/v1/media/{media_id}/info/",headers=HEADERS,cookies=COOKIES)
                status = response.json()["status"]
                if status == "fail":
                    data = session.get(fixed_url,cookies=COOKIES,headers=HEADERS)
                    ig_user_id = data.json()["user"]["id"]
                    if not is_highlight:
                        return await download_highlights_and_stories(is_story=True,tg_user_id=user_id,user_id=ig_user_id,media_id=media_id)
                    else:
                        return await download_highlights_and_stories(is_highlight=True,tg_user_id=user_id,user_id=ig_user_id,media_id=media_id[0],highlight_id=media_id[1])
            
            status = response.json()["status"]

            if status == "fail":
                return await bot.send_message(user_id,'Media not found')
            
            data = response.json()["items"][0]

            media_type = data["media_type"]
        
            if media_type == 1:
                url = data["image_versions2"]["candidates"][0]["url"]
                await send_photo(user_id,url)
        
            elif media_type == 2: 
                video_versions = data["video_versions"]
                url = video_versions[0]["url"]
                await send_video(user_id,url)

            elif media_type == 8:
                carousel_media = data["carousel_media"]
                await send_photos(user_id,carousel_media)
            
            else:
                await bot.send_message(user_id,"Invalid link.")

        except (KeyError,aiogram.utils.exceptions.InvalidHTTPUrlContent):
            if not is_story:
                try:
                    if len(video_versions) > 1:
                        url = video_versions[2]["url"]
                    if len(video_versions) == 1:
                        url = video_versions[1]["url"]
                
                    return await bot.send_video(user_id,url,caption="<i>@igviddwdbot</i>",parse_mode='HTML')
                except Exception as e:
                    await bot.send_message(user_id,"Video size is too big.\nMax video size is 50MB")
                    log.info(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
            await bot.send_message(user_id,"Invalid link.")
        except Exception as e:
            log.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            await bot.send_message(user_id,"Invalid link.")
    else:
        await bot.send_message(user_id,'Invalid link.')

async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    try:
        await bot.send_message(user_id,text,disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False

@dp.message_handler(state=Form.message)
async def broadcaster(message: types.Message, state: FSMContext):
    """Message Broadcaster"""

    # Finish our conversation
    await state.finish()
    count = 0
    try:
        for user in db.get_users():
            if await send_message(user["user_id"],message.text):
                count += 1
            await asyncio.sleep(.05) # 20 messages per second (Limit: 30 messages per second)
    finally:
        await bot.send_message(ADMIN_ID,f"{count} messages successfully sent.")
        log.info(f"{count} messages successfully sent.")

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)
