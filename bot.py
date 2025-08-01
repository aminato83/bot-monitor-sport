import json
import asyncio
import feedparser
import requests
import logging
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
from telegram import Bot

# 🛡️ Disattiva warning inutili
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 🔐 Dati Telegram
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = 7660020792
bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da cercare
KEYWORDS = [
    "infortunio", "infortuni", "infortunato", "infortunata", "infortunati", "infortunate",
    "squalifica", "squalificato", "squalificata", "squalificati", "squalificate",
    "espulso", "espulsi", "espulsa", "espulse",
    "problemi economici", "problemi finanziari", "fallimento", "fallimenti",
    "stipendi non pagati", "stipendi arretrati", "mensilità non pagate", "debiti",
    "crisi societaria", "crisi tecnica", "problemi societari", "problemi di formazione",
    "lite interna", "ritiro annullato", "ritiro cancellato", "ritiro saltato",
    "preparazione in ritardo", "precampionato in ritardo", "ritiro in ritardo",
    "covid", "virus", "positivi", "contagiati", "influenza",
    "assenze", "assenze pesanti", "giocatori assenti", "assenze importanti",
    "formazione rimaneggiata", "formazione d'emergenza", "rosa ridotta",
    "rosa corta", "panchina corta", "solo primavera", "solo riserve",
    "giocano con la primavera", "gioca la primavera", "giocano le riserve",
    "giocano solo riserve", "fanno giocare la primavera", "fanno giocare le riserve",
    "scendono in campo con la primavera", "scendono in campo con le riserve",
    "problemi interni", "problemi nello spogliatoio",
    "ammutinamento", "sciopero", "sciopero allenamenti", "allenamenti annullati",
    "ritardo preparazione", "ritardi nella preparazione",
    "assenze per squalifica", "assenze per infortunio",
    "squadra in crisi", "problemi nello staff", "problemi con l'allenatore",
    "giocatori separati in casa", "squadra sfavorita", "squadra rimaneggiata"
]

# 📁 File per evitare duplicati
INVIATE_FILE = "inviate.json"

def carica_fonti():
    with open("sources.json", "r", encoding="utf-8") as f:
        return json.load(f)

def carica_inviate():
    try:
        with open(INVIATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def salva_inviate(ids):
    with open(INVIATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)

# 🔎 Analisi dei feed RSS
async def analizza_fonti(fonti):
    gia_inviate = carica_inviate()
    nuove = set()

    for sport, fonti_sport in fonti.items():
        for url in fonti_sport:
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.content, "html.parser")
                feed = feedparser.parse(str(soup))

                for entry in feed.entries:
                    testo = f"{entry.title.lower()} {entry.get('summary', '').lower()}"
                    if any(k in testo for k in KEYWORDS):
                        id_unico = entry.get("id") or entry.get("link")
                        if id_unico and id_unico not in gia_inviate:
                            messaggio = f"🚨 [{sport.upper()}] {entry.title}\n🔗 {entry.link}"
                            await bot.send_message(chat_id=CHAT_ID, text=messaggio)
                            logging.info(f"📨 Inviato su Telegram: {messaggio}")
                            nuove.add(id_unico)
                await asyncio.sleep(1)
            except Exception as e:
                logging.warning(f"⚠️ Errore con {url}: {e}")

    if nuove:
        gia_inviate.update(nuove)
        salva_inviate(gia_inviate)

# 🔁 Loop continuo ogni 10 minuti
async def loop():
    while True:
        logging.info("🔁 Avvio scansione fonti RSS...")
        fonti = carica_fonti()
        await analizza_fonti(fonti)
        await asyncio.sleep(600)

# 🚀 Avvio del bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    asyncio.run(loop())
