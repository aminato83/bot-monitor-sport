import os
import asyncio
import logging
import requests
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# 🔧 Carica variabili ambiente (opzionale)
load_dotenv()

# 📌 CONFIGURAZIONE TELETHON (sessione utente)
API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"

# 📌 CONFIGURAZIONE BOT TELEGRAM (MonitorSportAlert_bot)
BOT_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
ALERT_CHAT_ID = 7660020792  # Gruppo/canale dove inviare gli alert

# ✅ CANALI DA MONITORARE (verificati + test)
CHANNELS_TO_MONITOR = [
    "serieDHCWP",
    "serieDofficial",
    "SerieCPassionHub",
    "seriednews",
    "serieCnews",
    "legavolley",
    "legavolleyfemminile",
    "calcioSerieCD",      # test
    "calciominorecd"      # test
]

# 🧠 PAROLE CHIAVE DA RILEVARE
KEYWORDS = [
    "infortunio", "problema", "assenza", "non convocato", "multa", "fallimento", "ritiro",
    "ritiro squadra", "partita annullata", "stadio chiuso", "penalizzazione", "debiti",
    "tifosi infuriati", "assenze importanti", "squalifica", "indisponibile", "dimissioni",
    "esonero", "campo neutro", "senza pubblico", "problemi societari",
    "finestra di mercato chiuso", "giocheranno giovani", "pignoramento"
]

# ✅ MESSAGGI GESTITI (per evitare duplicati)
MESSAGGI_GESTITI = set()


async def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
    logging.info("🚀 Avvio monitoraggio canali Telegram...")

    # Avvia il client Telethon
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    # 🔁 TEST INVIO ALERT ALL'AVVIO
    try:
        test_msg = "📢 Monitoraggio attivo. Questo è un messaggio di test dal bot `telegram_monitor.py`."
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ALERT_CHAT_ID,
            "text": test_msg
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info("📨 Messaggio di test inviato con successo.")
        else:
            logging.warning(f"⚠️ Errore nell'invio del messaggio di test: {response.text}")
    except Exception as e:
        logging.error(f"❌ Errore nell'invio del messaggio di test: {e}")

    # 📥 GESTIONE NUOVI MESSAGGI
    @client.on(events.NewMessage)
    async def handler(event):
        try:
            msg_id = event.message.id
            chat_id = event.chat_id
            unique_key = f"{chat_id}-{msg_id}"

            if unique_key in MESSAGGI_GESTITI:
                return

            sender = await event.get_chat()
            message_text = event.message.message.lower()

            for keyword in KEYWORDS:
                if keyword in message_text:
                    alert_text = (
                        f"🚨 Parola chiave trovata: *{keyword}*\n"
                        f"📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({chat_id})\n\n"
                        f"📝 Messaggio:\n{event.message.message}"
                    )
                    # Invia il messaggio con il BOT API
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data={
                            "chat_id": ALERT_CHAT_ID,
                            "text": alert_text,
                            "parse_mode": "Markdown"
                        }
                    )
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    MESSAGGI_GESTITI.add(unique_key)
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


# 🎬 Esegui
if __name__ == "__main__":
    asyncio.run(main())
