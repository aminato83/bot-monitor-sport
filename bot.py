import json
import asyncio
import feedparser
import requests
import logging
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
from telegram import Bot

# 🔕 Disattiva warning BeautifulSoup
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# 🔐 Dati Telegram - MonitorSportAlert_bot
TELEGRAM_TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"
CHAT_ID = -1002120185621  # <-- Sostituisci con il tuo se diverso

bot = Bot(token=TELEGRAM_TOKEN)

# 🧠 Parole chiave da rilevare
KEYWORDS = [
    "infortunio", "infortunato", "infortunati", "lesione", "lesioni", "stop fisico",
    "rottura crociato", "rottura legamenti", "problema muscolare", "stiramento", "strappo",
    "fastidio fisico", "acciacco", "non convocato", "non disponibili", "assente", "assenti",
    "out", "fuori rosa", "assenza", "assenze", "indisponibile", "indisponibili",

    "squalifica", "squalificato", "squalificati", "espulsione", "espulso", "espulsi",
    "ammonizione", "ammonito", "cartellino rosso", "cartellino giallo", "diffidato",
    "sanzione disciplinare", "provvedimento disciplinare",

    "formazione rimaneggiata", "formazione d'emergenza", "rosa ridotta", "rosa corta",
    "rosa in difficoltà", "mancano titolari", "senza titolari", "con le riserve",
    "formazione primavera", "giocano le riserve", "giocano con la primavera",
    "giocano con la squadra primavera", "fanno giocare la primavera",
    "fanno giocare la squadra primavera", "fanno giocare le riserve",
    "scelte obbligate", "turnover",

    "problemi societari", "problemi economici", "problemi finanziari", "stipendi non pagati",
    "stipendi arretrati", "mensilità non pagate", "debiti", "fallimento", "rischio fallimento",
    "penalizzazione", "punti di penalizzazione", "ritiro squadra", "sciopero",
    "ritiro precampionato", "ritardo precampionato", "stipendi in ritardo", "società in crisi",
    "squadra in crisi", "crisi finanziaria", "problemi con la dirigenza", "lite interna",

    "lite in spogliatoio", "clima teso", "tensioni interne", "giocatori contro allenatore",
    "esonero imminente", "contestazione tifosi", "clima negativo", "crisi tecnica",
    "crisi di risultati", "senza vittorie", "morale basso",

    "esonero", "esonerato", "cambio allenatore", "nuovo tecnico", "nuova guida",
    "allenatore ad interim", "debutto allenatore", "debutto panchina", "prima partita nuovo allenatore",

    "maltempo", "campo impraticabile", "partita rinviata", "partita a rischio", "partita sospesa",
    "neve", "pioggia", "vento forte", "allerta meteo", "problemi di trasporto", "ritardo viaggio",
    "guasto pullman", "trasferta difficile",

    "positivo covid", "positivi al covid", "covid", "focolaio", "quarantena", "isolamento",
    "assenza per covid", "caso covid", "contagiati", "emergenza sanitaria", "tampone positivo",

    "problemi di tesseramento", "documenti non pronti", "indisponibile per tesseramento",
    "problemi di passaporto", "giocatore non schierabile", "fuori lista", "mercato in uscita"
]

]

# 📁 File per evitare duplicati
INVIATE_FILE = "inviate.json"

# 🔄 Caricamento fonti da sources.json
def carica_fonti():
    with open("sources.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 🔄 Caricamento titoli già inviati
def carica_inviate():
    try:
        with open(INVIATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# 💾 Salvataggio titoli inviati
def salva_inviate(ids):
    with open(INVIATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)

# 🔍 Analisi feed
async def analizza_fonti(fonti):
    gia_inviate = carica_inviate()
    nuove = set()

    for sport, urls in fonti.items():
        for url in urls:
            try:
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.content, "html.parser")
                feed = feedparser.parse(str(soup))

                for entry in feed.entries:
                    titolo = entry.title.lower()
                    sommario = entry.get("summary", "").lower()
                    contenuto = f"{titolo} {sommario}"

                    if any(k in contenuto for k in KEYWORDS):
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

# 🔁 Loop infinito ogni 10 minuti
async def loop():
    while True:
        logging.info("🔁 Avvio scansione fonti RSS...")
        fonti = carica_fonti()
        await analizza_fonti(fonti)
        logging.info("⏳ Attendo 10 minuti prima della prossima scansione.")
        await asyncio.sleep(600)

# ▶️ Avvio
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    asyncio.run(loop())
