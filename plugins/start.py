import random
import humanize
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import *
from utils import temp, get_shortlink
from fsub import get_fsub
from info import *

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    is_banned, ban_reason = await db.is_user_banned(message.from_user.id)
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if FSUB and not await get_fsub(client, message):return
    if is_banned:
        await message.reply_text(f"Our system has detected some suspicious activity from your account, so you have been automatically banned. \n\nReason: {ban_reason}. \n\nContact @champaklalbot for assistance.")
        return
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/dsrbotzz")
        ],[
            InlineKeyboardButton("✨ Backup Channel", url="https://t.me/devbots2")
        ]] 
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )
    return


@Client.on_message(filters.private | filters.group | (filters.bot & filters.group) & (filters.document | filters.video))
async def stream_start(client, message):
    if message.command and message.command[0] == "broadcast":
        return
    is_banned, ban_reason = await db.is_user_banned(message.from_user.id)
    if is_banned:
        await message.reply_text(f"You are banned from using this bot for the following Reason: {ban_reason}. \n\nContact @champaklalbot for more assistance.")
        return

    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size) 
    fileid = file.file_id
    user_id = message.from_user.id
    username =  message.from_user.mention 

    try:
        print(f"DEBUG: Attempting to send file to LOG_CHANNEL: {LOG_CHANNEL}")
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
        print(f"DEBUG: Successfully sent to LOG_CHANNEL. Message ID: {log_msg.id}")
    except Exception as e:
        print(f"DEBUG: Failed to send to LOG_CHANNEL: {e}")
        await message.reply_text(f"Error: Could not send file to log channel. Make sure the bot is an admin in the log channel ({LOG_CHANNEL}).\nError details: {e}")
        return

    if LOG_CHANNEL_2 and LOG_CHANNEL_2 != 0:
        try:
            print(f"DEBUG: Attempting to send file to LOG_CHANNEL_2: {LOG_CHANNEL_2}")
            log_msg_2 = await client.send_cached_media(
                chat_id=LOG_CHANNEL_2,
                file_id=fileid,
            )
            print(f"DEBUG: Successfully sent to LOG_CHANNEL_2. Message ID: {log_msg_2.id}")
            await db.save_file_mapping(log_msg.id, log_msg_2.id)
            print(f"DEBUG: Saved file mapping: Primary {log_msg.id} -> Backup {log_msg_2.id}")
        except Exception as e:
            print(f"DEBUG: Failed to send to LOG_CHANNEL_2: {e}")
            # Don't return, just log the error. Primary channel worked.

    fileName = {quote_plus(get_name(log_msg))}

    unprotected_stream_url = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
    unprotected_download_url = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

    has_password = await db.get_password(message.from_user.id)
    password = None
    if has_password:
        try:
            password_message = await client.ask(chat_id=message.from_user.id, text="Please send the password for this file.", timeout=60)
            password = password_message.text
            temp.PASS[str(log_msg.id)] = {"password": password, "stream_url": unprotected_stream_url, "download_url": unprotected_download_url}
        except: #If the user fails to send the password within 60 seconds
            return
    else:
        temp.PASS[str(log_msg.id)] = {"password": None, "stream_url": unprotected_stream_url, "download_url": unprotected_download_url}
    if FSUB and not await get_fsub(client, message):return
    if SHORTLINK == False:
        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}")
        download = await get_shortlink(f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}")
        
    if has_password and password:
        direct_stream_url = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}&password={password}"
        direct_download_url = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}&password={password}"
        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName} \n\n•• ᴘᴀssᴡᴏʀᴅ : {password}\n\n•• ᴅɪʀᴇᴄᴛ sᴛʀᴇᴀᴍ : {direct_stream_url}\n•• ᴅɪʀᴇᴄᴛ ᴅᴏᴡɴʟᴏᴀᴅ : {direct_download_url}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                                                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]])  # web stream Link
        )
    else:
        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}\n\n•• ᴜɴᴘʀᴏᴛᴇᴄᴛᴇᴅ sᴛʀᴇᴀᴍ : {unprotected_stream_url}\n•• ᴜɴᴘʀᴏᴛᴇᴄᴛᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ : {unprotected_download_url}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # we download Link
                                                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)]])  # web stream Link
        )
    rm=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
            ]
        ] 
    )
    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

    await message.reply_text(text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(message)), download, stream), quote=True, disable_web_page_preview=True, reply_markup=rm)

@Client.on_message(filters.command('stats') & filters.user(ADMINS) & filters.incoming)
async def get_ststs(bot, message):
    users = await db.total_users_count()
    await message.reply_text(script.STATUS_TXT.format(users))