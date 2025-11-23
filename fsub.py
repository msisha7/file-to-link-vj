from typing import List
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton , CallbackQuery
from pyrogram.types import Message
from pyrogram.client import Client
from pyrogram import enums
from utils import temp
from pyrogram.enums import ChatMemberStatus
from info import *
from database.users_chats_db import *
from Script import script

FORCE_SUB_CHANNEL = -1001802883067  # Replace with your channel ID
FORCE_SUB_CHANNEL2 = -1001788629657  # Replace with your second channel ID (optional)

async def get_fsub(bot: Client, message: Message) -> bool:
    user_id = message.from_user.id

    # Allow admins to bypass subscription checks
    if user_id in ADMINS:
        return True

    # Track the join status for each channel
    channel_status = {
        "channel1": False,
        "channel2": False,
    }
    join_buttons = []

    # Check subscription for FORCE_SUB_CHANNEL
    if FORCE_SUB_CHANNEL:
        try:
            member = await bot.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
            if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                channel_status["channel1"] = True
            else:
                raise Exception("Not a valid member")
        except:
            channel_link = (await bot.get_chat(FORCE_SUB_CHANNEL)).invite_link
            join_buttons.append(InlineKeyboardButton("Join Channel 1", url=channel_link))

    # Check subscription for FORCE_SUB_CHANNEL2
    if FORCE_SUB_CHANNEL2:
        try:
            member = await bot.get_chat_member(chat_id=FORCE_SUB_CHANNEL2, user_id=user_id)
            if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                channel_status["channel2"] = True
                
            else:
                raise Exception("Not a valid member")
        except:
            channel_link = (await bot.get_chat(FORCE_SUB_CHANNEL2)).invite_link
            join_buttons.append(InlineKeyboardButton("Join Channel 2", url=channel_link))

    # Add a Refresh button
    refresh_button = InlineKeyboardButton("Refresh ♻", url="https://t.me/Dsr_File2link_Bot?start=start")

    # Determine which message to send based on join status
    if not channel_status["channel1"] and not channel_status["channel2"]:
        # Polite message when both channels are not joined
        keyboard: List[List[InlineKeyboardButton]] = [join_buttons, [refresh_button]]
        await message.reply(
            f"<b>Dear {message.from_user.mention},\n\n"
            f"Due to overload only our channel members can use this bot. Join our channels to use the bot! 😊</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return False
    elif not channel_status["channel1"] or not channel_status["channel2"]:
        # Strict message when one channel is skipped
        keyboard: List[List[InlineKeyboardButton]] = [join_buttons, [refresh_button]]
        await message.reply(
            f"<b>Don't be oversmart 😒, {message.from_user.mention}!\n\n"
            f"You must join both of our channels to use this bot! 😊</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return False

    return True

async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if FSUB and not await get_fsub(client, message):return
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


@Client.on_callback_query()
async def handle_callback_query(bot: Client, callback_query: CallbackQuery):
    if callback_query.data == "refresh":
        # Delete the old message to avoid clutter
        await callback_query.message.delete()

        # Create a mock message object from the callback query to pass to `get_fsub`
        mock_message = callback_query.message
        mock_message.from_user = callback_query.from_user

        # Re-run the subscription check
        if await get_fsub(bot, mock_message):
            # If user joined both channels, call startcmd
            await start(client, mock_message)



# Start command handler
