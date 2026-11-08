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

    # 1. Kirim pesan status awal sebagai penanda progres tahap 1
    status_message = await context.bot.send_message(
        chat_id=chat_id, 
        text="📥 **Status:** Pesan diterima. Menyiapkan sistem..."
    )
    message_id = status_message.message_id

    try:
        # 2. Update status ke tahap koneksi API
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="⚙️ **Status:** Menghubungkan ke OpenRouter API & memproses AI..."
        )

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

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_data = response.json()
        
        if "choices" in res_data:
            reply_text = res_data["choices"][0]["message"]["content"]
        else:
            reply_text = f"⚠️ Error dari OpenRouter: {res_data.get('error', 'Unknown error')}"

        # 3. Update status tahap akhir sebelum menampilkan jawaban penuh
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🚀 **Status:** Menyusun jawaban akhir..."
        )

        # Kirim hasil akhir (opsional: jika teks terlalu panjang, telegram otomatis memecah atau kirim langsung)
        # Kita edit pesan status terakhir menjadi jawaban dari AI
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=reply_text
        )

    except Exception as e:
        # Tangani jika terjadi error di tengah jalan
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ Gagal terhubung ke API: {str(e)}"
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 AI Agent Berjalan di Termux... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()
    
