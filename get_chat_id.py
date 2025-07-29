from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8224474749:AAE8sg_vC7HFFq1oJMKowtbTFwwwoH4QHwU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print("✅ Chat ID trovato:", chat_id)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Ora vai su Telegram e scrivi /start al tuo bot")
    app.run_polling()
