import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
import os
from telegram import Bot

# --- CONFIGURAZIONE ---
KEYWORDS = [
    "infortunio", "infortuni", "infortunato", "infortunati", "squalifica", "squalificato", "squalificati",
    "espulso", "espulsi", "espulsioni", "problemi economici", "problemi finanziari", "fallimento", "fallimenti",
    "stipendi non pagati", "mensilità non pagate", "debiti", "precampionato in ritardo", "preparazione in ritardo",
    "stipendi arretrati", "giornate di squalifica", "problemi di formazione", "virus", "covid", "allenamenti annullati",
    "problemi societari", "lite interna", "crisi tecnica"
]

CHAT_ID = "6635379606"  # <-- tuo chat ID
BOT_TOKEN = "6711468996:AAEeU9TWvLRvo5KDOiQgKqP0DWZ5U8wv_WI"  # <-- tuo bot token

bot = Bot(token=BOT_TOKEN)

# --- CARICAMENTO FONTI ---
with open("sources.json", "r", encoding="utf-8") as f:
    fonti = json.load(f)

# --- FILE NOTIZIE GIÀ INVIATE ---
FILE_INVIATE = "inviate.json"
if not os.path.exists(FILE_INVIATE):
    with open(FILE_INVIATE, "w", encoding="utf-8") as f:
        json.dump([], f)

def notizia_gia_inviata(link, notizie_gia_inviate):
    return link in notizie_gia_inviate

def salva_link_inviato(link, notizie_gia_inviate):
    notizie_gia_inviate.append(link)
    with open(FILE_INVIATE, "w", encoding="utf-8") as f:
        json.dump(notizie_gia_inviate, f)

def contiene_keywords(testo):
    testo = testo.lower()
    return any(kw in testo for kw in KEYWORDS)

def analizza_fonti(fonti):
    with open(FILE_INVIATE, "r", encoding="utf-8") as f:
        try:
            notizie_gia_inviate = json.load(f)
        except json.decoder.JSONDecodeError:
            notizie_gia_inviate = []

    for fonte in fonti:
        categoria = fonte["categoria"]
        url = fonte["url"]
        selettore = fonte["selettore"]

        print(f"🔍 Analizzando notizie per: {categoria.upper()}")

        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            articoli = soup.select(selettore)

            for articolo in articoli:
                titolo = articolo.get_text(strip=True)
                link = articolo.get("href")
                if not link.startswith("http"):
                    link = url.rstrip("/") + "/" + link.lstrip("/")

                if contiene_keywords(titolo) and not notizia_gia_inviata(link, notizie_gia_inviate):
                    messaggio = f"🚨 [{categoria.upper()}] {titolo}\n🔗 {link}"
                    bot.send_message(chat_id=CHAT_ID, text=messaggio)
                    print(f"📨 Inviato su Telegram: {titolo}")
                    salva_link_inviato(link, notizie_gia_inviate)

        except Exception as e:
            print(f"⚠️ Errore durante l'analisi di {url}: {e}")

# --- SCHEDULAZIONE ---
def job():
    analizza_fonti(fonti)

print("⏳ Il bot è in esecuzione. Controlla ogni 10 minuti...")
schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
