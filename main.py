import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "nousresearch/hermes-3-llama-3.1-405b:free")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    # Kirim indikator mengetik ke Telegram
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Request ke OpenRouter API (Nous Hermes / Model Open Source)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
        "X-Title": "Moto G57 AI Agent",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten AI pribadi yang cerdas, efisien, dan berjalan di server HP Android Moto G57."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_data = response.json()
        
        if "choices" in res_data:
            reply_text = res_data["choices"][0]["message"]["content"]
        else:
            reply_text = f"⚠️ Error dari OpenRouter: {res_data.get('error', 'Unknown error')}"
    except Exception as e:
        reply_text = f"❌ Gagal terhubung ke API: {str(e)}"

    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 AI Agent Berjalan di Termux... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

