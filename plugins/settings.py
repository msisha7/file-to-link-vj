
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db

@Client.on_message(filters.command("settings"))
async def settings(client, message):
    is_banned, _ = await db.is_user_banned(message.from_user.id)
    if is_banned:
        await message.reply_text(f"You are banned from using this bot.")
        return
    has_password = await db.get_password(message.from_user.id)
    
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Password", callback_data="password"),
            InlineKeyboardButton("✅" if has_password else "❌", callback_data="toggle_password")
        ]]
    )
    
    await client.send_message(
        chat_id=message.from_user.id,
        text="Configure your settings for the bot.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^toggle_password$"))
async def toggle_password(client, callback_query: CallbackQuery):
    has_password = await db.get_password(callback_query.from_user.id)
    await db.set_password(callback_query.from_user.id, not has_password)
    has_password = not has_password
    
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Password", callback_data="password"),
            InlineKeyboardButton("✅" if has_password else "❌", callback_data="toggle_password")
        ]]
    )
    
    await callback_query.message.edit_reply_markup(reply_markup=rm)
