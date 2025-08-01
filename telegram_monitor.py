import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv
import requests

# Carica variabili da .env (opzionale)
load_dotenv()

# 📌 CONFIGURAZIONE UTENTE (SESSIONE UTENTE TELEGRAM)
API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"

# 📢 CONFIGURAZIONE BOT TELEGRAM UFFICIALE
BOT_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"  # MonitorSportAlert_bot
CHAT_ID = "-1002138972697"  # Chat ID del canale MonitorSportAlert

# ✅ CANALI DA MONITORARE
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

# 🧠 PAROLE CHIAVE
KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari", "finestra di mercato chiuso", "giocheranno giovani", "pignoramento"
]

# 🧠 Messaggi già inviati per evitare duplicati
seen_messages = set()

# 🚀 AVVIO MONITORAGGIO
async def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    # ✅ Messaggio di test all'avvio
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": "🟢 Monitoraggio canali Telegram attivo.",
                "parse_mode": "Markdown"
            }
        )
        if response.status_code == 200:
            logging.info("📨 Messaggio di test inviato con successo.")
        else:
            logging.warning(f"⚠️ Errore nell'invio del messaggio di test: {response.text}")
    except Exception as e:
        logging.error(f"❌ Errore nell'invio del messaggio di test: {e}")

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            message_id = (event.chat_id, event.id)
            if message_id in seen_messages:
                return
            seen_messages.add(message_id)

            sender = await event.get_chat()
            message_text = event.message.message.lower()
            logging.debug(f"📩 Nuovo messaggio ricevuto da {getattr(sender, 'title', 'Sconosciuto')}: {message_text}")

            for keyword in KEYWORDS:
                if keyword in message_text:
                    alert_text = (
                        f"🚨 *Parola chiave trovata*: `{keyword}`\n"
                        f"📣 *Canale*: {getattr(sender, 'title', 'Sconosciuto')} (`{event.chat_id}`)\n\n"
                        f"📝 *Messaggio:*\n{event.message.message}"
                    )
                    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": CHAT_ID,
                        "text": alert_text,
                        "parse_mode": "Markdown"
                    }
                    response = requests.post(send_url, data=payload)
                    if response.status_code == 200:
                        logging.info(f"🔔 ALERT inviato: {keyword}")
                    else:
                        logging.warning(f"⚠️ Errore nell'invio dell'alert: {response.text}")
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # ➕ UNISCITI AI CANALI
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

# 🎬 ESECUZIONE
if __name__ == "__main__":
    asyncio.run(main())
