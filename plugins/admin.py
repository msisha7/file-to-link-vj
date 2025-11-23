from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS
from database.users_chats_db import db

@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user(client: Client, message: Message):
    try:
        if len(message.command) < 3:
            await message.reply_text("Usage: /ban user_id reason")
            return
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:])
        await db.ban_user(user_id, reason)
        await client.send_message(
            chat_id=user_id,
            text=f"Our system has detected some suspicious activity from your account, so you have been automatically banned. \n\nReason: {reason}. \nnContact @champaklalbot for assistance."
        )
        await message.reply_text(f"User {user_id} has been banned.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("Usage: /unban user_id")
            return
        user_id = int(message.command[1])
        await db.unban_user(user_id)
        await client.send_message(
            chat_id=user_id,
            text=f"Your account has been unbanned. You can now use the bot."
        )
        await message.reply_text(f"User {user_id} has been unbanned.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_message_to_user(client: Client, message: Message):
    try:
        if len(message.command) < 3:
            await message.reply_text("Usage: /send user_id message")
            return
        user_id = int(message.command[1])
        msg_to_send = " ".join(message.command[2:])
        await client.send_message(
            chat_id=user_id,
            text=msg_to_send
        )
        await message.reply_text(f"Message sent to {user_id}.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
