from telethon.sync import TelegramClient

# ✅ I tuoi dati di accesso personali
api_id = 23705599
api_hash = 'c472eb3f5c85a74f99bec9aa3cfef294'

# 📁 Nome del file di sessione (verrà creato automaticamente)
session_name = 'monitor_session'

# ⚙️ Crea la sessione e avvia il login
with TelegramClient(session_name, api_id, api_hash) as client:
    print("✅ Login effettuato con successo!")
