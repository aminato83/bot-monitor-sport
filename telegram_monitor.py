import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio
import telegram

# 📦 Carica variabili da .env
load_dotenv()
API_ID = int(os.getenv("API_ID", "23705599"))
API_HASH = os.getenv("API_HASH", "c472eb3f5c85a74f99bec9aa3cfef294")
SESSION_NAME = "telegram_monitor"

# 🔐 Token e Chat ID per bot ufficiale
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU")
CHAT_ID = int(os.getenv("ALERT_CHAT_ID", "7660020792"))  # Canale o gruppo ricevente

# 🔎 Parole chiave da cercare
KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari", "finestra di mercato chiuso",
    "giocheranno giovani", "pignoramento"
]

# 📣 Canali da monitorare
CHANNELS_TO_MONITOR = [
    "serieDHCWP",
    "serieDofficial",
    "SerieCPassionHub",
    "seriednews",
    "serieCnews",
    "legavolley",
    "legavolleyfemminile",
    "calcioSerieCD",
    "calciominorecd"
]

# 🔁 Per evitare duplicati
processed_message_ids = set()

# 🚀 Funzione principale
async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

    # Test: invio messaggio per verificare che funzioni
    try:
        await bot.send_message(chat_id=CHAT_ID, text="📡 Monitoraggio attivo (telegram_monitor.py)")
        logging.info("📨 Messaggio di test inviato con successo.")
    except Exception as e:
        logging.error(f"❌ Errore nell'invio del messaggio di test: {e}")

    # 📩 Listener per nuovi messaggi
    @client.on(events.NewMessage)
    async def handler(event):
        message_id = event.message.id
        chat_id = event.chat_id

        if (chat_id, message_id) in processed_message_ids:
            return  # messaggio già gestito

        processed_message_ids.add((chat_id, message_id))

        try:
            sender = await event.get_chat()
            message_text = event.message.message.lower()

            for keyword in KEYWORDS:
                if keyword in message_text:
                    alert_text = (
                        f"🚨 Parola chiave trovata: *{keyword}*\n"
                        f"📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({event.chat_id})\n\n"
                        f"📝 Messaggio:\n{event.message.message}"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=alert_text, parse_mode=telegram.constants.ParseMode.MARKDOWN)
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # ➕ Unisciti ai canali
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

# ▶️ Avvia lo script
if __name__ == "__main__":
    asyncio.run(main())
