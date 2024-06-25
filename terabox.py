from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import logging
import asyncio
from pyrogram.enums import ChatMemberStatus
from dotenv import load_dotenv
import os
from status import format_progress_bar  # Ensure these modules are available
from video import download_video, upload_video  # Ensure these modules are available
from web import keep_alive  # Ensure this module is available

# Load environment variables from a file named config.env
load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)

# Read and validate environment variables
try:
    api_id = int(os.environ.get('TELEGRAM_API', '0'))
    if api_id == 0:
        raise ValueError("TELEGRAM_API is not set or invalid")

    api_hash = os.environ.get('TELEGRAM_HASH', '')
    if not api_hash:
        raise ValueError("TELEGRAM_HASH is not set or invalid")

    bot_token = os.environ.get('BOT_TOKEN', '')
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set or invalid")

    dump_id = int(os.environ.get('DUMP_CHAT_ID', '0'))
    if dump_id == 0:
        raise ValueError("DUMP_CHAT_ID is not set or invalid")

    fsub_id = int(os.environ.get('FSUB_ID', '0'))
    if fsub_id == 0:
        raise ValueError("FSUB_ID is not set or invalid")
except ValueError as e:
    logging.error(f"Environment variable error: {e}")
    exit(1)

# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define bot behavior
@app.on_message(filters.command("start"))
async def start_command(client, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEYonplzwrczhVu3I6HqPBzro3L2JU6YAACvAUAAj-VzAoTSKpoG9FPRjQE")
    await asyncio.sleep(2)
    await sticker_message.delete()
    user_mention = message.from_user.mention
    reply_message = f"ᴡᴇʟᴄᴏᴍᴇ, {user_mention}.\n\n🌟 ɪ ᴀᴍ ᴀ ᴛᴇʀᴀʙᴏx ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ. sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ ɪ ᴡɪʟʟ ᴅᴏᴡɴʟᴏᴀᴅ ᴡɪᴛʜɪɴ ғᴇᴡ sᴇᴄᴏɴᴅs ᴀɴᴅ sᴇɴᴅ ɪᴛ ᴛᴏ ʏᴏᴜ ✨."
    join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/VijayTv_SerialVideos")
    developer_button = InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ⚡️", url="https://t.me/VijayTv_SerialVideos")
    reply_markup = InlineKeyboardMarkup([[join_button, developer_button]])
    await message.reply_text(reply_message, reply_markup=reply_markup)

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
    user_id = message.from_user.id
    user_mention = message.from_user.mention
    is_member = await is_user_member(client, user_id)

    if not is_member:
        join_button = InlineKeyboardButton("ᴊᴏɪɴ ❤️🚀", url="https://t.me/VijayTv_SerialVideos")
        reply_markup = InlineKeyboardMarkup([[join_button]])
        await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴍʏ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ.", reply_markup=reply_markup)
        return

    terabox_link = message.text.strip()
    if "terabox" not in terabox_link:
        await message.reply_text("ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴛᴇʀᴀʙᴏx ʟɪɴᴋ.")
        return

    reply_msg = await message.reply_text("sᴇɴᴅɪɴɢ ʏᴏᴜ ᴛʜᴇ ᴍᴇᴅɪᴀ...🤤")

    try:
        file_path, thumbnail_path, video_title = await download_video(terabox_link, reply_msg, user_mention, user_id)
        await upload_video(client, file_path, thumbnail_path, video_title, reply_msg, dump_id, user_mention, user_id, message)
    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await reply_msg.edit_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ.\nɪғ ʏᴏᴜʀ ғɪʟᴇ sɪᴢᴇ ɪs ᴍᴏʀᴇ ᴛʜᴀɴ 120ᴍʙ ɪᴛ ᴍɪɢʜᴛ ғᴀɪʟ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ.\nᴛʜɪs ɪs ᴛʜᴇ ᴛᴇʀᴀʙᴏx ɪssᴜᴇ, sᴏᴍᴇ ʟɪɴᴋs ᴀʀᴇ ʙʀᴏᴋᴇɴ, sᴏ ᴅᴏɴᴛ ᴄᴏɴᴛᴀᴄᴛ ʙᴏᴛ's ᴏᴡɴᴇʀ")

if __name__ == "__main__":
    keep_alive()
    app.run()
    
