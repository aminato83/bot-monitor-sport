import json
import time
import feedparser
import schedule
import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
from telegram import Bot

# 🔕 Disattiva warning XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 🔐 Dati del bot
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792

bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare
parole_chiave = [
    "infortunio", "infortuni", "infortunato", "infortunati",
    "squalifica", "squalificato", "squalificati", "espulso", "espulsi", "espulsioni",
    "problemi economici", "problemi finanziari", "fallimento", "fallimenti",
    "stipendi non pagati", "mensilitá non pagate", "debiti", "stipendi arretrati",
    "precampionato in ritardo", "preparazione in ritardo", "giornate di squalifica",
    "problemi di formazione", "virus", "covid", "allenamenti annullati",
    "problemi societari", "lite interna", "crisi tecnica"
]

# 📁 File per tracciare notizie inviate
file_inviate = 'inviate.json'

# 📥 Carica le fonti RSS
def carica_fonti():
    with open('sources.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# 📚 Carica ID notizie già inviate
def carica_inviate():
    try:
        with open(file_inviate, 'r', encoding='utf-8') as file:
            return set(json.load(file))
    except:
        return set()

# 💾 Salva ID notizie inviate
def salva_inviate(lista):
    with open(file_inviate, 'w', encoding='utf-8') as file:
        json.dump(list(lista), file, ensure_ascii=False, indent=2)

# 🔎 Analizza feed
def analizza_fonti(fonti):
    notizie_gia_inviate = carica_inviate()
    nuove_inviate = set()

    for sport, fonti_sport in fonti.items():
        print(f"\n🔍 Analizzando notizie per: {sport.upper()}")
        for fonte in fonti_sport:
            url = fonte.get("url") if isinstance(fonte, dict) else fonte
            try:
                risposta = requests.get(url, timeout=10)
                soup = BeautifulSoup(risposta.content, 'html.parser')
                feed = feedparser.parse(str(soup))

                for notizia in feed.entries:
                    titolo = notizia.title.lower()
                    descrizione = notizia.get("summary", "").lower()
                    testo = f"{titolo} {descrizione}"

                    if any(parola in testo for parola in parole_chiave):
                        id_notizia = notizia.get("id") or notizia.get("link")

                        if id_notizia and id_notizia not in notizie_gia_inviate:
                            messaggio = f"🚨 [{sport.upper()}] {notizia.title}\n🔗 {notizia.link}"
                            bot.send_message(chat_id=CHAT_ID, text=messaggio)
                            print("📨 Inviato su Telegram:", messaggio)
                            nuove_inviate.add(id_notizia)

                time.sleep(1)  # Attesa tra le fonti

            except Exception as e:
                print(f"⚠️ Errore nel sito {url} — {e}")

    # 🔄 Salvataggio notizie nuove
    if nuove_inviate:
        notizie_gia_inviate.update(nuove_inviate)
        salva_inviate(notizie_gia_inviate)

# 🚀 Esegui analisi
def job():
    fonti = carica_fonti()
    analizza_fonti(fonti)

# ⏱️ Ogni 10 minuti
schedule.every(10).minutes.do(job)

print("⏳ Il bot è in esecuzione. Controlla ogni 10 minuti...")
job()  # Avvio iniziale

# 🔁 Loop continuo
while True:
    schedule.run_pending()
    time.sleep(1)
