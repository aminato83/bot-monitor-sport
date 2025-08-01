import asyncio
...

# 🔎 Analizza feed
async def analizza_fonti(fonti):
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
                            await bot.send_message(chat_id=CHAT_ID, text=messaggio)
                            print("📨 Inviato su Telegram:", messaggio)
                            nuove_inviate.add(id_notizia)

                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Errore nel sito {url} — {e}")

    if nuove_inviate:
        notizie_gia_inviate.update(nuove_inviate)
        salva_inviate(notizie_gia_inviate)

# 🚀 Esegui analisi
async def job():
    fonti = carica_fonti()
    await analizza_fonti(fonti)

# ⏱️ Avvio
if __name__ == '__main__':
    print("⏳ Il bot è in esecuzione. Controlla ogni 10 minuti...")

    async def loop():
        while True:
            await job()
            await asyncio.sleep(600)  # 10 minuti

    asyncio.run(loop())
