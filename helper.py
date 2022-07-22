from config import bot,dp
import requests as r
import re
import os
from urllib.parse import urlparse
import asyncio
import logging
import base64

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def is_valid(url: str):
    allowed_links = [
        r"https://www.instagram.com/tv/",
        r"https://instagram.com/tv/",
        r"https://www.instagram.com/p/",
        r"https://instagram.com/p/",
        r"https://www.instagram.com/reel/",
        r"https://instagram.com/reel/",
        r"https://www.instagram.com/stories/",
        r"https://instagram.com/stories/",
        r"https://www.instagram.com/s/",
        r"https://instagram.com/s/"
    ]
    matches = [re.match(link,url) for link in allowed_links]
    for match in matches:
        if match != None:
            return True
    else:
        return False

async def prepare_urls(matches):
    return list({match.replace("\\u0026", "&") for match in matches})

async def normalize_url(url: str):
    uri = urlparse(url)
    scheme = uri.scheme
    netloc = uri.netloc
    path = uri.path
    query = "?__a=1&__d=dis"
    fixed_url = f"{scheme}://{netloc}{path}{query}"

    path = uri.path.split("/")
    sp = uri.query.split("&")
    media_id = re.findall(r'story_media_id=([^"]+)',sp[0])
    
    if path[2] == "highlights" and path[1] != "s":
        media_id = path[3]
        return True,True,media_id,fixed_url

    elif path[1] == "stories" and path[1] != "s":
        media_id = path[3]
        return True,False,media_id,fixed_url

    elif path[1] == "s":
        highlight = base64.b64decode(path[2])
        decoded_highlight = highlight.decode("utf-8")
        highlights,highlight_id = decoded_highlight.split(":")

        media_id = media_id[0].split("_")
        return True,True,(media_id[0],decoded_highlight),f"https://www.instagram.com/stories/highlights/{highlight_id}/?__a=1&__d=dis"

    return False,False,media_id,fixed_url
