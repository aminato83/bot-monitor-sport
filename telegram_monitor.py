import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# Carica variabili da .env (facoltativo ma consigliato)
load_dotenv()

# 📌 Configurazione
API_ID = 23705599
API_HASH = "c472eb3f5c85a74f99bec9aa3cfef294"
SESSION_NAME = "telegram_monitor"
ALERT_CHAT_ID = 7660020792  # ✅ Chat ID corretto

# 📡 Canali Telegram da monitorare
CHANNELS_TO_MONITOR = [
    "serieDHCWP",
    "serieDofficial",
    "SerieCPassionHub",
    "seriednews",
    "serieditalia",
    "seried_live",
    "seriecmagazine",
    "serieCnews",
    "serie_c_live",
    "volleyball_it",
    "legavolley",
    "legavolleyfemminile",
    "volley_news",
    "LNPitalia",
    "basketseriea",
    "basketinside",
    "divisionecalcioa5",
    "futsalnews",
    "pallamanotv",
    "figh_press"
]

# 🧠 Parole chiave da rilevare
KEYWORDS = [
    "infortunio", "infortuni", "infortunato", "infortunati",
    "assenza", "non convocato", "assenze importanti",
    "multa", "squalifica", "espulso", "espulsi", "dimissioni",
    "fallimento", "ritiro", "partita annullata", "stadio chiuso",
    "penalizzazione", "debiti", "stipendi non pagati", "pignoramento",
    "tifosi infuriati", "problemi societari", "problemi economici",
    "campo neutro", "senza pubblico", "indisponibile", "lite interna"
]

# 🚀 Avvio monitoraggio
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
                    alert_text = (
                        f"🚨 Parola chiave trovata: *{keyword}*\n"
                        f"📣 Canale: {getattr(sender, 'title', 'Sconosciuto')} ({event.chat_id})\n\n"
                        f"📝 Messaggio:\n{event.message.message}"
                    )
                    await client.send_message(ALERT_CHAT_ID, alert_text)
                    logging.info(f"🔔 ALERT inviato: {keyword}")
                    break

        except Exception as e:
            logging.error(f"❌ Errore nella gestione del messaggio: {e}")

    # 🔗 Unisciti ai canali (se necessario)
    for channel in CHANNELS_TO_MONITOR:
        try:
            await client(JoinChannelRequest(channel))
            logging.info(f"✅ Unito al canale: {channel}")
        except Exception as e:
            logging.warning(f"⚠️ Non riesco ad accedere al canale {channel}: {e}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
