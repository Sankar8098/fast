import requests
import asyncio
import os
import time
import logging
import subprocess
from datetime import datetime
from pymongo import MongoClient
import aria2p
from pyrogram import Client, filters
from status import format_progress_bar

# Telegram Bot API Credentials
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
COLLECTION_CHANNEL_ID = -1001234567890  # Replace with your channel ID

# MongoDB setup
mongo_client = MongoClient("mongodb+srv://sankar:sankar@sankar.lldcdsx.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["bot_database"]
downloads_collection = db["downloads"]
uploads_collection = db["uploads"]

# Aria2 setup
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=8000,
        secret=""
    )
)

# Initialize Pyrogram Client
app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to get video duration using ffmpeg
def get_video_duration(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return int(float(result.stdout.strip()))
    except Exception as e:
        logging.warning(f"Could not get video duration: {e}")
        return 0

async def download_video(url, reply_msg, user_mention, user_id):
    api_url = "https://yt.savetube.me/terabox-downloader"
    payload = {"url": url}

    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise Exception("Failed to fetch download details from API")

    video_info = data["response"][0]
    fast_download_link = video_info["url"]
    thumbnail_url = video_info["thumbnail"]
    video_title = video_info["title"]

    # Insert initial download record into MongoDB
    download_record = {
        "url": url,
        "video_title": video_title,
        "thumbnail_url": thumbnail_url,
        "user_mention": user_mention,
        "user_id": user_id,
        "start_time": datetime.now(),
        "status": "Downloading"
    }
    download_id = downloads_collection.insert_one(download_record).inserted_id

    download = aria2.add_uris([fast_download_link])
    start_time = datetime.now()

    while not download.is_complete:
        download.update()
        percentage = download.progress
        done = download.completed_length
        total_size = download.total_length
        speed = download.download_speed
        eta = download.eta
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()
        progress_text = format_progress_bar(
            filename=video_title,
            percentage=percentage,
            done=done,
            total_size=total_size,
            status="Downloading",
            eta=eta,
            speed=speed,
            elapsed=elapsed_time_seconds,
            user_mention=user_mention,
            user_id=user_id,
            aria2p_gid=download.gid
        )
        await reply_msg.edit_text(progress_text)
        await asyncio.sleep(2)

    if download.is_complete:
        file_path = download.files[0].path

        # Download thumbnail
        thumbnail_path = "thumbnail.jpg"
        thumbnail_response = requests.get(thumbnail_url)
        with open(thumbnail_path, "wb") as thumb_file:
            thumb_file.write(thumbnail_response.content)

        # Update download record status in MongoDB
        downloads_collection.update_one({"_id": download_id}, {"$set": {"status": "Completed", "file_path": file_path, "end_time": datetime.now()}})

        await reply_msg.edit_text("Uploading...")

        return file_path, thumbnail_path, video_title
    else:
        downloads_collection.update_one({"_id": download_id}, {"$set": {"status": "Failed", "end_time": datetime.now()}})
        raise Exception("Download failed")

async def upload_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    # Get video duration using ffmpeg
    duration = get_video_duration(file_path)
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    conv_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

    # Insert initial upload record into MongoDB
    upload_record = {
        "video_title": video_title,
        "file_path": file_path,
        "thumbnail_path": thumbnail_path,
        "user_mention": user_mention,
        "user_id": user_id,
        "start_time": datetime.now(),
        "status": "Uploading"
    }
    upload_id = uploads_collection.insert_one(upload_record).inserted_id

    async def progress(current, total):
        nonlocal uploaded, last_update_time
        uploaded = current
        percentage = (current / total) * 100
        elapsed_time_seconds = (datetime.now() - start_time).total_seconds()

        if time.time() - last_update_time > 2:
            progress_text = format_progress_bar(
                filename=video_title,
                percentage=percentage,
                done=current,
                total_size=total,
                status="Uploading",
                eta=(total - current) / (current / elapsed_time_seconds) if current > 0 else 0,
                speed=current / elapsed_time_seconds if current > 0 else 0,
                elapsed=elapsed_time_seconds,
                user_mention=user_mention,
                user_id=user_id,
                aria2p_gid=""
            )
            try:
                await reply_msg.edit_text(progress_text)
                last_update_time = time.time()
            except Exception as e:
                logging.warning(f"Error updating progress message: {e}")

    with open(file_path, 'rb') as file:
        collection_message = await client.send_video(
            chat_id=collection_channel_id,
            video=file,
            duration=duration,
            caption=f"✨ {video_title} \n⏰ Duration: {conv_duration} \n👤 Leached by: {user_mention}\n📥 User link: tg://user?id={user_id}",
            thumb=thumbnail_path,
            progress=progress
        )
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=collection_channel_id,
            message_id=collection_message.id
        )
        await asyncio.sleep(1)
        await message.delete()

    await reply_msg.delete()
    os.remove(file_path)
    os.remove(thumbnail_path)

    uploads_collection.update_one({"_id": upload_id}, {"$set": {"status": "Completed", "end_time": datetime.now()}})
    return collection_message.id

@app.on_message(filters.command("download"))
async def handle_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a TeraBox link.")
        return

    url = message.command[1]
    reply_msg = await message.reply_text("Processing...")
    user_mention = message.from_user.mention
    user_id = message.from_user.id

    await handle_download_and_upload(url, reply_msg, user_mention, user_id, client, COLLECTION_CHANNEL_ID, message)

app.run()
