import json
import os
import asyncio
import re
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from telethon.errors.common import TypeNotFoundError
from datetime import datetime
import logging
import time

# Logging base
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# Carica configurazioni
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "monitor")
TELEGRAM_ALERT_CHAT_ID = int(os.getenv("TELEGRAM_ALERT_CHAT_ID"))

# File contenente i canali da monitorare
CHANNELS_FILE = "telegram_channels.json"
# File per tenere traccia dei messaggi già inviati
MESSAGES_SENT_FILE = "sent_telegram_messages.json"

# Parole chiave importanti
KEYWORDS = [
    "infortun", "assente", "problema", "problemi", "squalific", "riserve",
    "non convocato", "fuori", "assenza", "crisi", "debito", "fallimento",
    "società in crisi", "problemi economici", "stipendi", "indisponibile"
]

# Carica messaggi già inviati
def carica_messaggi_gia_inviati():
    if os.path.exists(MESSAGES_SENT_FILE):
        with open(MESSAGES_SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# Salva messaggi già inviati
def salva_messaggi_gia_inviati(messaggi):
    with open(MESSAGES_SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(messaggi), f, ensure_ascii=False)

# Funzione filtro intelligente
def contiene_keyword_testo(text):
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if re.search(rf"\b{keyword}\b", text_lower):
            return True
    return False

# Avvio monitoraggio
async def main():
    logging.info("🚀 Avvio monitoraggio canali Telegram...")
    
    # Carica i canali
    if not os.path.exists(CHANNELS_FILE):
        logging.error(f"❌ File {CHANNELS_FILE} non trovato.")
        return
    
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels = json.load(f)
    
    messaggi_inviati = carica_messaggi_gia_inviati()

    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        while True:
            for channel in channels:
                try:
                    entity = await client.get_entity(channel)
                    messages = await client.get_messages(entity, limit=10)

                    for message in messages:
                        if message.id and str(message.id) not in messaggi_inviati:
                            testo = message.message or ""
                            if contiene_keyword_testo(testo):
                                link = f"https://t.me/{channel.replace('@', '')}/{message.id}"
                                alert = f"📢 Nuova segnalazione da {channel}:\n\n{testo}\n\n🔗 {link}"
                                await client.send_message(TELEGRAM_ALERT_CHAT_ID, alert)
                                logging.info(f"✅ Messaggio inviato: {alert[:80]}...")
                                messaggi_inviati.add(str(message.id))
                    
                except TypeNotFoundError as e:
                    logging.warning(f"⚠️ TypeNotFoundError su {channel}: {str(e)}")
                except Exception as e:
                    logging.error(f"❌ Errore nel canale {channel}: {e}")

                # Attendi 3 secondi prima del prossimo canale
                time.sleep(3)

            # Salva i messaggi già inviati ogni ciclo
            salva_messaggi_gia_inviati(messaggi_inviati)

            logging.info("🔁 Attendo 10 minuti prima del prossimo ciclo...")
            await asyncio.sleep(600)  # 10 minuti

if __name__ == "__main__":
    asyncio.run(main())
