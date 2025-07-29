import instaloader
import time
import json
import os
import schedule
from datetime import datetime

# Configurazioni
USERNAME = "misterc_tips"
SESSION_FILE = os.path.expanduser("~/.instaloader/session-{}".format(USERNAME))
PROFILI = [
    "seriec", "seried_24", "seriedignorante", "corner.jpeg",
    "legaseriecofficial", "seriecofficial", "seried_official",
    "tuttoseried", "seriecnews"
]
PAROLE_CHIAVE = ["infortunio", "assenza", "problema", "squalifica", "non convocato"]
POSTS_GIA_INVIATI_FILE = "instagram_gia_inviati.json"

# Carica i post già inviati
if os.path.exists(POSTS_GIA_INVIATI_FILE):
    with open(POSTS_GIA_INVIATI_FILE, "r") as f:
        posts_gia_inviati = json.load(f)
else:
    posts_gia_inviati = []

# Invia notifica (personalizza questa funzione con Telegram)
def invia_notifica(post):
    print(f"📢 Nuovo post rilevante da {post['autore']}: {post['url']}")

# Analizza post di un singolo profilo
def analizza_profilo(instaloader_instance, profilo):
    try:
        print(f"🔍 Controllando profilo: {profilo}")
        account = instaloader.Profile.from_username(instaloader_instance.context, profilo)
        for post in account.get_posts():
            url = f"https://www.instagram.com/p/{post.shortcode}/"
            if url in posts_gia_inviati:
                continue
            didascalia = post.caption or ""
            testo = didascalia.lower()
            if any(parola in testo for parola in PAROLE_CHIAVE):
                invia_notifica({"autore": profilo, "url": url, "testo": didascalia})
                posts_gia_inviati.append(url)
                with open(POSTS_GIA_INVIATI_FILE, "w") as f:
                    json.dump(posts_gia_inviati, f)
            time.sleep(5)  # ⏳ Pausa tra un post e l'altro
    except Exception as e:
        print(f"⚠️ Errore su {profilo}: {e}")

# Ciclo principale di controllo
def analizza_instagram():
    print(f"\n{datetime.now().strftime('%H:%M:%S')} 🚀 Monitoraggio Instagram avviato...")
    L = instaloader.Instaloader()
    try:
        L.load_session_from_file(USERNAME, SESSION_FILE)
    except:
        print("⚠️ Sessione non trovata. Effettua il login con: instaloader --login=misterc_tips")
        return

    for profilo in PROFILI:
        analizza_profilo(L, profilo)
        time.sleep(30)  # ⏳ Pausa tra i profili

# Avvia subito e programma ogni 20 minuti
analizza_instagram()
schedule.every(20).minutes.do(analizza_instagram)

while True:
    schedule.run_pending()
    time.sleep(1)
