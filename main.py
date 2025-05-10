import asyncio
import random
import datetime
import json
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Telegram API credentials
api_id = 20596103
api_hash = "59e406718099f7eb5041371fed2cb3a1"

# Group and channel IDs
source_group = -1001725037486  # Source group ID
destination_channel = -1002513897184  # Destination channel ID

# File for storing forwarded media IDs
FORWARDED_FILE = 'forwarded_media.json'

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Load or initialize forwarded media
if os.path.exists(FORWARDED_FILE):
    with open(FORWARDED_FILE, 'r') as f:
        forwarded_media = json.load(f)
else:
    forwarded_media = {}

forward_count = 0

def save_forwarded_media():
    with open(FORWARDED_FILE, 'w') as f:
        json.dump(forwarded_media, f)

def is_media_forwarded(media_id):
    return media_id in forwarded_media

def mark_media_as_forwarded(media_id):
    forwarded_media[media_id] = str(datetime.datetime.now())
    save_forwarded_media()

async def forward_media(message):
    global forward_count
    try:
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            if isinstance(message.media, MessageMediaPhoto):
                media_id = f"photo_{message.media.photo.id}"
            elif isinstance(message.media, MessageMediaDocument):
                media_id = f"doc_{message.media.document.id}"
            else:
                return

            if is_media_forwarded(media_id):
                print(f"⏩ Already forwarded: {media_id}")
                return

            await client.send_file(destination_channel, message.media, caption=f" {forward_count}")
            mark_media_as_forwarded(media_id)
            forward_count += 1
            print(f"✅ Forwarded #{forward_count}: {media_id}")
            await asyncio.sleep(random.uniform(0.2, 0.3))
    except Exception as e:
        if "A wait of" in str(e):
            wait_time = int(str(e).split("A wait of ")[1].split(" ")[0])
            print(f"⏳ Rate limit hit, sleeping for {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        else:
            print(f"⚠ Error: {e}")

@client.on(events.NewMessage(chats=source_group))
async def forward_new_messages(event):
    await forward_media(event.message)

async def forward_old_messages():
    print("🚀 Forwarding old media...")
    count = 0
    media_seen = 0
    async for message in client.iter_messages(source_group, reverse=True):
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            media_seen += 1
            if media_seen <= 2:  # Skip first N messages
                continue
            await forward_media(message)
            count += 1
            if count % 1000 == 0:
                print("⏳ Cooldown: 60 seconds")
                await asyncio.sleep(60)
    print(f"✅ Finished. Forwarded: {count}, Seen: {media_seen}")

async def main():
    await client.start()
    print("📡 Bot started.")
    await forward_old_messages()
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
