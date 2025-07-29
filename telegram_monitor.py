import os
import json
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# Caricamento delle variabili d'ambiente
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME", "anon")
ALERT_CHAT_ID = int(os.getenv("ALERT_CHAT_ID"))
CHANNELS_FILE = os.getenv("CHANNELS_FILE", "telegram_channels.json")
KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.json")
PHONE_OR_TOKEN = os.getenv("PHONE_OR_TOKEN")

# Funzione per caricare i canali da monitorare
def load_channels():
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Errore nel caricamento dei canali: {e}")
        return []

# Funzione per caricare le keyword
def load_keywords():
    try:
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Errore nel caricamento delle keywords: {e}")
        return []

# Funzione principale asincrona
async def main():
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    if PHONE_OR_TOKEN:
        await client.start(phone=lambda: PHONE_OR_TOKEN)
    else:
        await client.start()

    channels = load_channels()
    keywords = load_keywords()

    # Monitoraggio messaggi nei canali
    @client.on(events.NewMessage(chats=channels))
    async def handler(event):
        text = event.raw_text.lower()
        for keyword in keywords:
            if keyword.lower() in text:
                link = f"https://t.me/{event.chat.username}/{event.id}" if event.chat.username else "Messaggio privato"
                messaggio = f"🔍 *Keyword trovata:* `{keyword}`\n📢 *Canale:* {event.chat.title}\n🕒 *Data:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🔗 *Link:* {link}"
                try:
                    await client.send_message(ALERT_CHAT_ID, messaggio, parse_mode="markdown")
                    logging.info(f"Inviato alert per keyword: {keyword}")
                except Exception as e:
                    logging.error(f"Errore nell'invio dell'alert: {e}")
                break

    await client.run_until_disconnected()

# Avvia lo script
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot interrotto manualmente.")
