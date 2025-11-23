import jinja2
from info import *
from TechVJ.bot import TechVJBot
from TechVJ.util.human_readable import humanbytes
from TechVJ.util.file_properties import get_file_ids
from TechVJ.server.exceptions import InvalidHash
from urllib.parse import quote_plus
import logging
import aiohttp
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "template")

async def render_page(id: int, secure_hash: str, password_protected: bool = False, template_name: str = "req.html", unprotected_stream_url: str = None, unprotected_download_url: str = None):
    if password_protected:
        template_file = "password_prompt.html"
    else:
        template_file = template_name

    with open(os.path.join(TEMPLATE_DIR, template_file)) as f:
        template = jinja2.Template(f.read())

    file_data = await get_file_ids(TechVJBot, LOG_CHANNEL, id)
    if not file_data:
        raise InvalidHash("Invalid file ID or hash.")

    file_name = file_data.file_name
    file_size = file_data.file_size
    
    if unprotected_stream_url and unprotected_download_url:
        file_url = unprotected_stream_url
        download_url = unprotected_download_url
    else:
        from utils import temp
        password_data = temp.PASS.get(str(id))
        file_url = f"/{id}/{quote_plus(file_name)}?hash={secure_hash}"
        if password_data and password_data.get("password"):
            file_url += f"&password={password_data['password']}"
        download_url = file_url

    return template.render(
        file_name=file_name,
        file_url=file_url,
        file_size=file_size,
        download_url=download_url
    )
