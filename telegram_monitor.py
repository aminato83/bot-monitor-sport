import os
import logging
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import requests

# Carica variabili da .env
load_dotenv()

API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"

# Bot Telegram ufficiale per invio alert
BOT_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = "7660020792"

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

KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari", "finestra di mercato chiuso",
    "giocheranno giovani", "pignoramento"
]

# Salva messaggi già visti per evitare duplicati
seen_message_ids = set()

async def send_alert(keyword, sender, message):
    alert_text = (
        f"🚨 Parola chiave trovata: *{keyword}*\n"
        f"📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({sender.id})\n\n"
        f"📝 Messaggio:\n{message}"
    )
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": alert_text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        if response.ok:
            logging.info(f"🔔 ALERT inviato: {keyword}")
        else:
            logging.error(f"❌ Errore nell'invio alert: {response.text}")
    except Exception as e:
        logging.error(f"❌ Errore nella richiesta HTTP: {e}")

async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    # Messaggio di test per confermare l’avvio
    test_msg = "✅ Monitoraggio attivo: il bot è online!"
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": test_msg}
        )
        logging.info("📨 Messaggio di test inviato con successo.")
    except Exception as e:
        logging.error(f"❌ Errore invio messaggio test: {e}")

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            message_id = event.id
            if message_id in seen_message_ids:
                return
            seen_message_ids.add(message_id)

            sender = await event.get_chat()
            message_text = event.message.message.lower()

            for keyword in KEYWORDS:
                if keyword in message_text:
                    await send_alert(keyword, sender, event.message.message)
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # Iscrizione ai canali
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
