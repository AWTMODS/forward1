import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Replace with your API credentials
api_id = 23393494
api_hash = "33847fcd7c06cb9ac91c2e4baa4b5c75"

# Group and channel IDs
source_group = -1002535791256
destination_channel = -1002368408222

# Initialize the client
client = TelegramClient('session_name', api_id, api_hash)

forward_count = 0

async def forward_media(message):
    """Forward only media files (images/documents)."""
    global forward_count
    try:
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            forward_count += 1
            await client.send_file(destination_channel, message.media, caption=f"{forward_count}")
            print(f"✅ Forwarded item {forward_count}")
            await asyncio.sleep(random.uniform(0.2, 0.3))
    except Exception as e:
        if "A wait of" in str(e):
            wait_time = int(str(e).split("A wait of ")[1].split(" ")[0])
            print(f"⏳ Rate limit hit! Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        else:
            print(f"⚠ Error: {e}")

@client.on(events.NewMessage(chats=source_group))
async def handler(event):
    await forward_media(event.message)

async def forward_old_messages():
    print("🚀 Forwarding old messages...")
    count = 0
    async for message in client.iter_messages(source_group, reverse=True):
        await forward_media(message)
        count += 1
        if count % 1000 == 0:
            print("⏳ Cooling down for 60 seconds...")
            await asyncio.sleep(60)
    print("✅ Done forwarding old messages.")

async def list_chats():
    """Optional: List all chats and their IDs."""
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        print(f"Name: {dialog.name}, ID: {dialog.id}")

async def main():
    await client.start()
    print("🚀 Client started.")
    # Uncomment this if you want to see your chat IDs
    await list_chats()
    await forward_old_messages()
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
