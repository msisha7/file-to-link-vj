# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
import datetime
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from database.users_chats_db import db
from info import ADMINS

# Enhanced and robust broadcast function with better logging, error handling, progress, and efficiency.

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    try:
        # Ask for the broadcast message
        b_msg = await bot.ask(
            chat_id=message.from_user.id,
            text="Now send me your broadcast message (text/media)."
        )
    except Exception as e:
        await message.reply("❌ Failed to get broadcast message.\n\nError: {}".format(e))
        return

    try:
        users = await db.get_all_users()
        total_users = await db.total_users_count()
        if total_users == 0:
            await message.reply("No users to broadcast to.")
            return

        sts = await message.reply_text('🔄 Broadcasting your message...')
        start_time = time.time()
        stats = {
            "done": 0,
            "success": 0,
            "blocked": 0,
            "deleted": 0,
            "failed": 0
        }
        batch_size = 20

        async for user in users:
            user_id = user.get('id')
            if user_id is not None:
                status, reason = await broadcast_messages(int(user_id), b_msg)
                if status:
                    stats["success"] += 1
                else:
                    if reason == "Blocked":
                        stats["blocked"] += 1
                    elif reason == "Deleted":
                        stats["deleted"] += 1
                    else:
                        stats["failed"] += 1
            else:
                stats["failed"] += 1  # No id, can't send

            stats["done"] += 1

            # Update status message every batch_size users
            if stats["done"] % batch_size == 0 or stats["done"] == total_users:
                await sts.edit(
                    f"📢 **Broadcast in progress:**\n\n"
                    f"👥 Total Users: `{total_users}`\n"
                    f"✅ Success: `{stats['success']}`\n"
                    f"⛔️ Blocked: `{stats['blocked']}`\n"
                    f"❌ Deleted: `{stats['deleted']}`\n"
                    f"⚠️ Failed: `{stats['failed']}`\n"
                    f"🔄 Completed: `{stats['done']} / {total_users}`"
                )

            # Optional: Add a small sleep to avoid hitting flood limits
            await asyncio.sleep(0.05)

        elapsed = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.edit(
            f"✅ **Broadcast Completed**\n\n"
            f"⏱ Time Taken: `{elapsed}`\n"
            f"👥 Total Users: `{total_users}`\n"
            f"✅ Success: `{stats['success']}`\n"
            f"⛔️ Blocked: `{stats['blocked']}`\n"
            f"❌ Deleted: `{stats['deleted']}`\n"
            f"⚠️ Failed: `{stats['failed']}`\n"
            f"🎯 Completed: `{stats['done']} / {total_users}`"
        )

    except Exception as e:
        logging.error(f"Broadcast error: {e}")
        await message.reply(f"❗️ An error occurred during broadcast:\n\n{e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def broadcast_messages(user_id, message):
    """
    Sends a copy of the message to the given user_id.
    Returns (True, "Success") on success,
    or (False, reason) on failure.
    """
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        logging.warning(f"FloodWait for {e.x} seconds for user {user_id}. Waiting...")
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from database (Deleted Account).")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid, removed from database.")
        return False, "Deleted"
    except Exception as e:
        logging.error(f"Failed to send message to {user_id}: {e}")
        return False, "Error"
