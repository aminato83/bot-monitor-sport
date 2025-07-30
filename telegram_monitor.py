import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"
ALERT_CHAT_ID = 6463144062

# ✅ SOLO canali verificati
CHANNELS_TO_MONITOR = [
    "serieDHCWP",
    "serieDofficial",
    "SerieCPassionHub"
]

KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari", "pignoramento"
]

async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            sender = await event.get_chat()
            message_text = event.message.message.lower()

            for keyword in KEYWORDS:
                if keyword in message_text:
                    alert_text = f"🚨 Parola chiave trovata: *{keyword}*\n📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({event.chat_id})\n\n📝 Messaggio:\n{event.message.message}"
                    await client.send_message(ALERT_CHAT_ID, alert_text)
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # (Facoltativo) Prova ad unirti ai canali
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
