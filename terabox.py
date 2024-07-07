from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from datetime import datetime
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
from os import environ
from web import keep_alive
import time
from status import format_progress_bar  # Assumed to be part of your project
from video import download_video, upload_video  # Assumed to be part of your project

load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

api_id = environ.get('TELEGRAM_API', '28192191')
if len(api_id) == 0:
    logging.error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)

api_hash = environ.get('TELEGRAM_HASH', '663164abd732848a90e76e25cb9cf54a')
if len(api_hash) == 0:
    logging.error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

bot_token = environ.get('BOT_TOKEN', '7198441390:AAFKm0aYuNbv_kWLesYFmtlLpC-nP5ogrbY')
if len(bot_token) == 0:
    logging.error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)
dump_id = environ.get('DUMP_CHAT_ID', '-1002149484754')
if len(dump_id) == 0:
    logging.error("DUMP_CHAT_ID variable is missing! Exiting now")
    exit(1)
else:
    dump_id = int(dump_id)

fsub_id = environ.get('FSUB_ID', '-1002249393777')
if len(fsub_id) == 0:
    logging.error("FSUB_ID variable is missing! Exiting now")
    exit(1)
else:
    fsub_id = int(fsub_id)

admin_id = environ.get('ADMIN_ID', 'YOUR_TELEGRAM_USER_ID')
if len(admin_id) == 0:
    logging.error("ADMIN_ID variable is missing! Exiting now")
    exit(1)
else:
    admin_id = int(admin_id)

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAJiHmZ-YWyuVu4snSoya1tYKXQJVd-BAAJBAAMh8AQcKgSvkt56N8E1BA")
    await asyncio.sleep(2)
    await sticker_message.delete()
    user_mention = message.from_user.mention if message.from_user else "User"
    reply_message = f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ", url="https://t.me/Semma_Bots")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ⚡️", url="https://t.me/Semma_Bots")
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])
    await message.reply_text(reply_message, reply_markup=reply_markup)

@app.on_message(filters.command("members_count") & filters.user(admin_id))
async def members_count(client, message):
    chat = await client.get_chat(fsub_id)
    await message.reply_text(f"The total number of members in the channel is: {chat.members_count}")

@app.on_message(filters.command("broadcast") & filters.user(admin_id))
async def broadcast_message(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to broadcast it.")
        return

    async for member in client.get_chat_members(fsub_id):
        try:
            await message.reply_to_message.copy(chat_id=member.user.id)
            await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Failed to send message to {member.user.id}: {e}")

    await message.reply_text("Broadcast completed.")

@app.on_message(filters.command("bot_status"))
async def bot_status(client, message):
    start_time = time.time()
    await message.reply_text("Checking bot status...")
    end_time = time.time()
    uptime = end_time - start_time
    await message.reply_text(f"Bot is running. Uptime: {uptime:.2f} seconds")

async def is_user_member(client, user_id):
    try:
        member = await client.get_chat_member(fsub_id, user_id)
        logging.info(f"User {user_id} membership status: {member.status}")
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking membership status for user {user_id}: {e}")
        return False

@app.on_message(filters.text)
async def handle_message(client, message: Message):
    if not message.from_user:
        await message.reply_text("Message does not have a valid user.")
        return

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ", url="https://t.me/Semma_Bots")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.", reply_markup=reply_markup)
        return

    terabox_link = message.text.strip()
    if "terabox" not in terabox_link and "terasharelink" not in terabox_link:
        await message.reply_text("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ᴏʀ ᴛᴇʀᴀsʜᴀʀᴇʟɪɴᴋ ʟɪɴᴋ.")
        return

    reply_msg = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...😉")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        unique_identifier = f"\nError ID: {int(time.time())}"  # Add unique identifier to the error message
        await edit_message(reply_msg, "ғᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ.\nɪғ ʏᴏᴜʀ ғɪʟᴇ sɪᴢᴇ ɪs ᴍᴏʀᴇ ᴛʜᴀɴ 120ᴍʙ ɪᴛ ᴍɪɢʜᴛ ғᴀɪʟ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ." + unique_identifier)

async def edit_message(message, new_text):
    if message.text != new_text:
        await message.edit_text(new_text)

if __name__ == "__main__":
    app.run()
