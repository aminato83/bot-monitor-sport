import json
import feedparser
from telegram import Bot
import schedule
import time
import os

# 🔐 Token del bot Telegram e tuo chat ID
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792

bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare nei feed
parole_chiave = [
    "infortunio", "infortuni", "infortunato", "infortunati",
    "squalifica", "squalificato", "squalificati", "espulso", "espulsi", "espulsioni",
    "problemi economici", "problemi finanziari", "fallimento", "fallimenti",
    "stipendi non pagati", "mensilità non pagate", "stipendi arretrati", "giornate di squalifica",
    "precampionato in ritardo", "preparazione in ritardo", "debiti", "problemi di formazione",
    "penalizzazione", "ritardo stipendi", "esonero", "società in crisi",
    "virus", "covid", "allenamenti annullati", "problemi societari", "lite interna", "crisi tecnica"
]

# 📁 File per tracciare notizie già inviate
file_inviate = 'inviate.json'

# 📥 Carica i feed RSS dal file sources.json
def carica_fonti():
    with open('sources.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 📤 Carica le notizie già inviate dal file JSON
def carica_inviate():
    if not os.path.exists(file_inviate):
        with open(file_inviate, 'w') as f:
            json.dump([], f)
    with open(file_inviate, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# 💾 Salva le notizie già inviate
def salva_inviate(lista):
    with open(file_inviate, 'w') as f:
        json.dump(lista, f)

# 🔎 Analizza i feed e cerca parole chiave
def analizza_fonti(fonti):
    notizie_trovate = 0
    notizie_gia_inviate = carica_inviate()

    for sport, urls in fonti.items():
        print(f"\n🔍 Analizzando notizie per: {sport.upper()}")
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for notizia in feed.entries:
                    titolo = notizia.title.lower()
                    descrizione = notizia.get("summary", "").lower()
                    testo = f"{titolo} {descrizione}"
                    link = notizia.link

                    if link in notizie_gia_inviate:
                        continue

                    if any(parola in testo for parola in parole_chiave):
                        messaggio = f"🚨 [{sport.upper()}] {notizia.title}\n🔗 {link}"
                        bot.send_message(chat_id=CHAT_ID, text=messaggio)
                        print("📨 Inviato su Telegram:", messaggio)
                        notizie_gia_inviate.append(link)
                        notizie_trovate += 1

                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Errore nel sito: {url} — {e}")

    salva_inviate(notizie_gia_inviate)

    if notizie_trovate == 0:
        print("🔄 Nessuna notizia rilevante trovata.")

# 🔁 Azione da ripetere ogni 10 minuti
def job():
    fonti = carica_fonti()
    analizza_fonti(fonti)

# ⏱️ Avvio del controllo ogni 10 minuti
schedule.every(10).minutes.do(job)

print("⏳ Il bot è in esecuzione. Controlla ogni 10 minuti...")

# 🔁 Loop continuo
while True:
    schedule.run_pending()
    time.sleep(1)
