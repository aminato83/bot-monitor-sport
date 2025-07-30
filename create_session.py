from telethon.sync import TelegramClient
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_OR_TOKEN = os.getenv("PHONE_OR_TOKEN")

client = TelegramClient("telegram_monitor", API_ID, API_HASH)
client.start(PHONE_OR_TOKEN)
print("✅ Sessione creata e salvata come telegram_monitor.session")
