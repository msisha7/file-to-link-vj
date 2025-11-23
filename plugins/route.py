# Don't Remove Credit @VJ_Botz

# Subscribe YouTube Channel For Amazing Bot @Tech_VJ

# Ask Doubt on telegram @KingVJ01



import re, math, logging, secrets, mimetypes, time

from info import *

from aiohttp import web

from aiohttp.http_exceptions import BadStatusLine

from TechVJ.bot import multi_clients, work_loads, TechVJBot

from TechVJ.server.exceptions import FIleNotFound, InvalidHash

from TechVJ import StartTime, __version__

from TechVJ.util.custom_dl import ByteStreamer

from TechVJ.util.time_format import get_readable_time

from TechVJ.util.render_template import render_page

from utils import temp
from database.users_chats_db import db



routes = web.RouteTableDef()



@routes.get("/")

async def root_route_handler(request):

    return web.json_response("BenFilterBot")





@routes.get(r"/watch/{path:\S+}")

async def watch_route_handler_get(request: web.Request):

    try:

        path = request.match_info["path"]

        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:

            secure_hash = match.group(1)

            id = int(match.group(2))

        else:

            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))

            secure_hash = request.rel_url.query.get("hash")



        password_data = temp.PASS.get(str(id))

        url_password = request.rel_url.query.get("password")



        if password_data and password_data["password"] and url_password != password_data["password"]:

            response_text = await render_page(id, secure_hash, password_protected=True)

            logging.info(

                f"Returning password protected stream page. Content type: text/html, Length: {len(response_text)}"

            )

            return web.Response(text=response_text, content_type="text/html")

        else:

            response_text = await render_page(

                id,

                secure_hash

            )

            logging.info(

                f"Returning unprotected stream page. Content type: text/html, Length: {len(response_text)}"

            )

            return web.Response(text=response_text, content_type="text/html")



    except InvalidHash as e:

        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:

        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):

        pass

    except Exception as e:

        logging.critical(e, exc_info=True)

        raise web.HTTPInternalServerError(text=str(e))





@routes.post(r"/watch/{path:\S+}")

async def watch_route_handler_post(request: web.Request):

    try:

        path = request.match_info["path"]

        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:

            secure_hash = match.group(1)

            id = int(match.group(2))

        else:

            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))

            secure_hash = request.rel_url.query.get("hash")



        password_data = temp.PASS.get(str(id))



        if password_data:

            if request.method == "POST":

                data = await request.post()

                if data.get("password") == password_data["password"]:

                    response_text = await render_page(

                        id,

                        secure_hash

                    )

                    logging.info(

                        f"Returning unprotected stream page after password. Content type: text/html, Length: {len(response_text)}"

                    )

                    return web.Response(text=response_text, content_type="text/html")

                else:

                    return web.Response(text="Incorrect password", status=403)

            else:

                return web.Response(

                    text=await render_page(id, secure_hash, password_protected=True),

                    content_type="text/html",

                )

        else:

            return web.Response(

                text=await render_page(id, secure_hash), content_type="text/html"

            )



    except InvalidHash as e:

        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:

        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):

        pass

    except Exception as e:

        logging.critical(e, exc_info=True)

        raise web.HTTPInternalServerError(text=str(e))





@routes.get(r"/{path:.+}")

async def download_route_handler_get(request: web.Request):

    try:

        path = request.match_info["path"]

        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:

            secure_hash = match.group(1)

            id = int(match.group(2))

        else:

            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))

            secure_hash = request.rel_url.query.get("hash")



        password = temp.PASS.get(str(id))

        url_password = request.rel_url.query.get("password")



        if password and password.get("password") and url_password != password["password"]:

            response_text = await render_page(id, secure_hash, password_protected=True)

            logging.info(

                f"Returning password protected download page. Content type: text/html, Length: {len(response_text)}"

            )

            return web.Response(text=response_text, content_type="text/html")

        else:

            logging.info(

                f"Returning unprotected download stream. ID: {id}, Hash: {secure_hash}"

            )

            return await media_streamer(request, id, secure_hash)



    except InvalidHash as e:

        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:

        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):

        pass

    except Exception as e:

        logging.critical(e, exc_info=True)

        raise web.HTTPInternalServerError(text=str(e))





@routes.post(r"/{path:\S+}")

async def download_route_handler_post(request: web.Request):

    try:

        path = request.match_info["path"]

        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:

            secure_hash = match.group(1)

            id = int(match.group(2))

        else:

            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))

            secure_hash = request.rel_url.query.get("hash")



        password_data = temp.PASS.get(str(id))



        if password_data:

            if request.method == "POST":

                data = await request.post()

                if data.get("password") == password_data["password"]:

                    logging.info(

                        f"Returning unprotected download stream after password. ID: {id}, Hash: {secure_hash}"

                    )

                    return await media_streamer(request, id, secure_hash)

                else:

                    return web.Response(text="Incorrect password", status=403)

            else:

                return web.Response(

                    text=await render_page(id, secure_hash, password_protected=True),

                    content_type="text/html",

                )

        else:

            return await media_streamer(request, id, secure_hash)



    except InvalidHash as e:

        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:

        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):

        pass

    except Exception as e:

        logging.critical(e, exc_info=True)

        raise web.HTTPInternalServerError(text=str(e))





@routes.get(r"/stream_source/{token}")

async def stream_source_handler(request: web.Request):

    token = request.match_info["token"]

    id = temp.DIRECT_ACCESS_TOKENS.get(token)



    if not id:

        raise web.HTTPForbidden(text="Invalid or expired stream token.")



    # Remove the token after use (or implement a timeout mechanism)

    del temp.DIRECT_ACCESS_TOKENS[token]



    file_data = await get_file_ids(TechVJBot, LOG_CHANNEL, id)

    if not file_data:

        raise FIleNotFound("File not found for stream source.")

    secure_hash = file_data.unique_id[:6]



    return await media_streamer(request, id, secure_hash)





class_cache = {}





async def media_streamer(request: web.Request, id: int, secure_hash: str):

    range_header = request.headers.get("Range", 0)



    index = min(work_loads, key=work_loads.get)

    faster_client = multi_clients[index]



    if MULTI_CLIENT:

        logging.info(f"Client {index} is now serving {request.remote}")



    if faster_client in class_cache:

        tg_connect = class_cache[faster_client]

        logging.debug(f"Using cached ByteStreamer object for client {index}")

    else:

        logging.debug(f"Creating new ByteStreamer object for client {index}")

        tg_connect = ByteStreamer(faster_client)

        class_cache[faster_client] = tg_connect

    logging.debug("before calling get_file_properties")
    try:
        file_id = await tg_connect.get_file_properties(id, LOG_CHANNEL)
    except Exception as e:
        logging.debug(f"Failed to get file properties from LOG_CHANNEL: {e}")
        # Try backup channel
        backup_id = await db.get_backup_id(id)
        if backup_id and LOG_CHANNEL_2 and LOG_CHANNEL_2 != 0:
            logging.debug(f"Found backup ID {backup_id}. Trying LOG_CHANNEL_2...")
            try:
                file_id = await tg_connect.get_file_properties(backup_id, LOG_CHANNEL_2)
            except Exception as e2:
                logging.debug(f"Failed to get file properties from LOG_CHANNEL_2: {e2}")
                raise e
        else:
            raise e
    
    logging.debug("after calling get_file_properties")



    if file_id.unique_id[:6] != secure_hash:

        logging.debug(f"Invalid hash for message with ID {id}")

        raise InvalidHash



    file_size = file_id.file_size



    if range_header:

        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")

        from_bytes = int(from_bytes)

        until_bytes = int(until_bytes) if until_bytes else file_size - 1

    else:

        from_bytes = request.http_range.start or 0

        until_bytes = (request.http_range.stop or file_size) - 1



    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):

        return web.Response(

            status=416,

            body="416: Range not satisfiable",

            headers={"Content-Range": f"bytes */{file_size}"},

        )



    chunk_size = 1024 * 1024

    until_bytes = min(until_bytes, file_size - 1)



    offset = from_bytes - (from_bytes % chunk_size)

    first_part_cut = from_bytes - offset

    last_part_cut = until_bytes % chunk_size + 1



    req_length = until_bytes - from_bytes + 1

    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    body = tg_connect.yield_file(

        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size

    )



    mime_type = file_id.mime_type

    file_name = file_id.file_name

    disposition = "attachment"



    if mime_type:

        if not file_name:

            try:

                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"

            except (IndexError, AttributeError):

                file_name = f"{secrets.token_hex(2)}.unknown"

    else:

        if file_name:

            mime_type = mimetypes.guess_type(file_id.file_name)

        else:

            mime_type = "application/octet-stream"

            file_name = f"{secrets.token_hex(2)}.unknown"



    return web.Response(

        status=206 if range_header else 200,

        body=body,

        headers={

            "Content-Type": f"{mime_type}",

            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",

            "Content-Length": str(req_length),

            "Content-Disposition": f'{disposition}; filename="{file_name}"',

            "Accept-Ranges": "bytes",

        },

                    )
