import json
import feedparser
from telegram import Bot
import schedule
import time

# 🔐 Token del bot Telegram e tuo chat ID
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792

bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare nei feed
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

# 📥 Carica i feed RSS dal file sources.json
def carica_fonti():
    with open('sources.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 🔎 Analizza i feed e cerca parole chiave, evitando doppioni
def analizza_fonti(fonti):
    notizie_trovate = 0

    # Carica link già inviati
    try:
        with open('inviate.json', 'r', encoding='utf-8') as f:
            notizie_gia_inviate = json.load(f)
    except FileNotFoundError:
        notizie_gia_inviate = []

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

                    if any(parola in testo for parola in parole_chiave) and link not in notizie_gia_inviate:
                        messaggio = f"🚨 [{sport.upper()}] {notizia.title}\n🔗 {link}"
                        bot.send_message(chat_id=CHAT_ID, text=messaggio)
                        print("📨 Inviato su Telegram:", messaggio)
                        notizie_gia_inviate.append(link)
                        notizie_trovate += 1

            except Exception as e:
                print(f"⚠️ Errore nel sito: {url} — {e}")
            time.sleep(1)

    # Salva link inviati
    with open('inviate.json', 'w', encoding='utf-8') as f:
        json.dump(notizie_gia_inviate, f, indent=2)

    # Nessuna notizia trovata
    if notizie_trovate == 0:
        bot.send_message(chat_id=CHAT_ID, text="🔄 Nessuna notizia rilevante trovata in questo ciclo.")
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
