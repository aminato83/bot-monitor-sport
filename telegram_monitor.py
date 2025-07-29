import json
import asyncio
from telethon import TelegramClient, events
from telegram import Bot

# 🔐 Inserisci i tuoi dati API di Telegram (da https://my.telegram.org)
api_id = 23705599
api_hash = 'c472eb3f5c85a74f99bec9aa3cfef294'

# 🔐 Bot Telegram per inviare notifiche
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792
bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare
parole_chiave = [
    "infortunio", "infortuni", "infortunato", "infortunati",
    "squalifica", "squalificato", "squalificati",
    "espulso", "espulsi", "espulsioni",
    "problemi economici", "problemi finanziari", "fallimento", "fallimenti",
    "stipendi non pagati", "mensilità non pagate", "stipendi arretrati",
    "debiti", "precampionato in ritardo", "preparazione in ritardo",
    "giornate di squalifica", "problemi di formazione",
    "problema fisico", "non convocato", "assenza", 
    "ritardo stipendi", "penalizzazione", "esonero", "società in crisi",
    "virus", "covid", "allenamenti annullati",
    "problemi societari", "lite interna", "crisi tecnica"
]

# 🔗 Carica i canali Telegram da monitorare
with open("telegram_channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

# 📁 Messaggi già inviati (per evitare duplicati)
try:
    with open('messaggi_telegram_inviati.json', 'r', encoding='utf-8') as f:
        messaggi_inviati = json.load(f)
except FileNotFoundError:
    messaggi_inviati = []

client = TelegramClient("monitor_session", api_id, api_hash)

@client.on(events.NewMessage(chats=channels))
async def handler(event):
    testo = event.message.message.lower()
    link = f"https://t.me/{event.chat.username}/{event.message.id}"

    if any(parola in testo for parola in parole_chiave) and link not in messaggi_inviati:
        messaggio = f"🚨 [TELEGRAM] {event.chat.title}\n📝 {event.message.message[:100]}...\n🔗 {link}"
        try:
            bot.send_message(chat_id=CHAT_ID, text=messaggio)
            print("📨 Inviato su Telegram:", messaggio)
            messaggi_inviati.append(link)

            # Aggiorna file
            with open('messaggi_telegram_inviati.json', 'w', encoding='utf-8') as f:
                json.dump(messaggi_inviati, f, indent=2)

        except Exception as e:
            print(f"⚠️ Errore nell'invio messaggio Telegram: {e}")

print("▶️ Monitoraggio canali Telegram avviato...")
client.start()
client.run_until_disconnected()
