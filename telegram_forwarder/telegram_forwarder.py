from telethon import TelegramClient, events
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")
SOURCE_CHAT = int(os.getenv("SOURCE_CHAT"))
DEST_CHAT = int(os.getenv("DEST_CHAT"))

# Create client
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=SOURCE_CHAT))
async def forward_message(event):
    msg = event.message.message
    await client.send_message(DEST_CHAT, msg)
    print(f"Forwarded: {msg[:60]}...")

async def main():
    print("Bot running...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
