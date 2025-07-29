import json
import asyncio
from telethon import TelegramClient, events
from telegram import Bot

# === CONFIGURAZIONI ===
api_id = 23705599
api_hash = 'c472eb3f5c85a74f99bec9aa3cfef294'
session_name = 'monitor_session'

TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792
bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare nei messaggi
parole_chiave = [
    "infortunio", "problema fisico", "squalificato",
    "non convocato", "assenza", "ritardo stipendi",
    "penalizzazione", "esonero", "società in crisi"
]

# 📥 Carica i canali da telegram_channels.json
def carica_canali():
    with open('telegram_channels.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 🧠 Verifica se il testo contiene una parola chiave
def contiene_parole_chiave(testo):
    testo = testo.lower()
    return any(parola in testo for parola in parole_chiave)

# 🤖 Invia messaggio su Telegram
def invia_alert(sport, testo, link=None):
    messaggio = f"🚨 [TELEGRAM - {sport.upper()}]\n{testo}"
    if link:
        messaggio += f"\n🔗 {link}"
    bot.send_message(chat_id=CHAT_ID, text=messaggio)
    print("📨 Inviato su Telegram:", messaggio)

# === AVVIO CLIENT TELETHON ===
client = TelegramClient(session_name, api_id, api_hash)

async def main():
    canali = carica_canali()

    @client.on(events.NewMessage())
    async def handler(event):
        try:
            sender = await event.get_sender()
            username = getattr(sender, 'username', '').lower()
            message_text = event.raw_text

            if contiene_parole_chiave(message_text):
                for sport, lista in canali.items():
                    for link in lista:
                        if username in link.lower():
                            invia_alert(sport, message_text)
                            return
        except Exception as e:
            print("❌ Errore nel gestore messaggi:", e)

    print("📡 Monitoraggio canali Telegram avviato...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
