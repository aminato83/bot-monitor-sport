import os
import asyncio
import logging
import requests
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"
BOT_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
ALERT_CHAT_ID = 7660020792

CHANNELS_TO_MONITOR = [
    "serieDHCWP", "serieDofficial", "SerieCPassionHub",
    "seriednews", "serieCnews", "legavolley",
    "legavolleyfemminile", "calcioSerieCD", "calciominorecd"
]

KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa",
    "fallimento", "ritiro", "ritiro squadra", "partita annullata",
    "stadio chiuso", "penalizzazione", "debiti", "tifosi infuriati",
    "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari",
    "finestra di mercato chiuso", "giocheranno giovani", "pignoramento"
]

# 🔒 Salviamo ID dei messaggi già inviati
sent_messages = set()

async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    # ✅ Invio messaggio di test
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": ALERT_CHAT_ID, "text": "✅ Monitoraggio attivo (test Telegram bot)", "parse_mode": "Markdown"}
        )
        logging.info("📨 Messaggio di test inviato con successo.")
    except Exception as e:
        logging.error(f"❌ Errore nell'invio del messaggio di test: {e}")

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            message_text = event.message.message.lower()
            unique_msg_id = (event.chat_id, event.id)

            if unique_msg_id in sent_messages:
                logging.info("⏩ Messaggio già inviato, ignorato.")
                return

            for keyword in KEYWORDS:
                if keyword in message_text:
                    sender = await event.get_chat()
                    alert_text = (
                        f"🚨 Parola chiave trovata: *{keyword}*\n"
                        f"📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({event.chat_id})\n\n"
                        f"📝 Messaggio:\n{event.message.message}"
                    )

                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data={"chat_id": ALERT_CHAT_ID, "text": alert_text, "parse_mode": "Markdown"}
                    )
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    sent_messages.add(unique_msg_id)

                    # Limita memoria usata (buffer temporaneo)
                    if len(sent_messages) > 1000:
                        sent_messages.clear()
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
