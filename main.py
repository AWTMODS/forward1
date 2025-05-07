import asyncio
import random
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Replace with your API credentials from my.telegram.org
api_id = 20596103  
api_hash = "59e406718099f7eb5041371fed2cb3a1"

# Replace with your group and channel IDs
source_group = -1001725037486 # Source group ID
destination_channel = -1002524675347 # Destination channel ID

# Initialize Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Counter for tracking forwarded items
forward_count = 0

async def forward_media(message):
    """Forward only media files (images, documents) without text or links."""
    global forward_count
    forward_count += 1

    try:
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            await client.send_file(destination_channel, message.media, caption=f"Item Forward {forward_count}")
            print(f"✅ Item {forward_count} forwarded successfully.")
            await asyncio.sleep(random.uniform(0.2, 0.3))  # Small delay to avoid spam detection
    except Exception as e:
        if "A wait of" in str(e):
            wait_time = int(str(e).split("A wait of ")[1].split(" ")[0])
            print(f"⏳ Rate limit hit! Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)  # Wait the required time
        else:
            print(f"⚠ Error forwarding item {forward_count}: {e}")

@client.on(events.NewMessage(chats=source_group))
async def forward_new_messages(event):
    """Forward new messages as they arrive."""
    await forward_media(event.message)

async def forward_old_messages():
    """Forward existing media messages from the group to the channel, starting after the 12891 media."""
    print("🚀 Starting to forward old media messages after the 12891th one...")
    count = 0
    media_seen = 0

    async for message in client.iter_messages(source_group, reverse=True):
        if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
            media_seen += 1
            if media_seen <= 21547:
                continue  # Skip first 3296 media messages

            await forward_media(message)
            count += 1

            if count % 1000 == 0:
                print("⏳ Waiting 60 seconds to avoid spam...")
                await asyncio.sleep(60)

    print("✅ Finished forwarding all media messages after 12891.")


async def main():
    await client.start()
    print("🚀 Bot is running... Forwarding messages.")
    await forward_old_messages()
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())




