import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telegram import Bot
from dotenv import load_dotenv

# Carica variabili da .env (se presenti)
load_dotenv()

# 📌 CREDENZIALI
API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"
BOT_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
ALERT_CHAT_ID = 7660020792  # Chat del canale MonitorSportAlert

# 📢 Canali da monitorare
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

# 🧠 Parole chiave
KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari", "finestra di mercato chiuso",
    "giocheranno giovani", "pignoramento"
]

# 🔁 Clienti
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot = Bot(token=BOT_TOKEN)

# 🚀 Funzione principale
async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    await client.start()

    # 🎯 Handler dei messaggi
    @client.on(events.NewMessage)
    async def handler(event):
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

                    await bot.send_message(chat_id=ALERT_CHAT_ID, text=alert_text, parse_mode="Markdown")
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # ➕ Iscriviti ai canali (facoltativo)
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

# ▶️ Avvio
if __name__ == "__main__":
    asyncio.run(main())
