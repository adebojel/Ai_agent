import os
import re
import subprocess
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "nousresearch/hermes-3-llama-3.1-405b:free")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    # 1. Kirim status awal
    status_message = await context.bot.send_message(
        chat_id=chat_id, 
        text="📥 **Status:** Pesan diterima. Menganalisis permintaan aplikasi..."
    )
    message_id = status_message.message_id

    try:
        # 2. Update status ke proses AI
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="⚙️ **Status:** Meminta AI merancang kode aplikasi & otomatisasi..."
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Agent",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "Kamu adalah Senior Software Engineer AI yang berjalan di Termux Android. "
            "Jika pengguna meminta untuk membuat sebuah aplikasi (seperti kalkulator, alat utilitas, dll), "
            "berikan kode program lengkapnya dalam blok kode Markdown (contoh: ```python ... ```). "
            "Sertakan juga nama file yang disarankan di dalam responsmu (contoh: `kalkulator.py`). "
            "Pastikan kodenya bersih, modular, dan bebas bug."
        )

        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res_data = response.json()
        
        if "choices" in res_data:
            reply_text = res_data["choices"][0]["message"]["content"]
        else:
            reply_text = f"⚠️ Error dari OpenRouter: {res_data.get('error', 'Unknown error')}"

        # 3. Update status tahap ekstraksi & penyimpanan file otomatis
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🚀 **Status:** Menyimpan file & melakukan sinkronisasi otomatis ke GitHub..."
        )

        # Cari blok kode python di dalam respons AI
        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", reply_text, re.DOTALL)
        
        # Cari nama file jika disebutkan AI atau pengguna (contoh: kalkulator.py)
        file_matches = re.findall(r"(?:simpan|nama file|file|bernama)[:\s]+`?([a-zA-Z0-9_\-]+\.py)`?", user_message.lower() + " " + reply_text.lower())
        filename = file_matches[0] if file_matches else "app_generated.py"

        if code_blocks:
            app_code = code_blocks[0]
            # Simpan file secara fisik di folder repository lokal Termux
            with open(filename, "w", encoding="utf-8") as f:
                f.write(app_code)

            # Jalankan otomatisasi Git (add, commit, push ke GitHub)
            subprocess.run(["git", "add", filename], capture_output=True)
            commit_msg = f"Auto-generated app: {filename} via Telegram bot"
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
            push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True)

            if push_result.returncode == 0:
                automation_status = f"\n\n✅ **Otomasi Berhasil!** File `{filename}` telah dibuat, di-push ke GitHub, dan sedang diproses GitHub Actions menjadi **Artifact & Release** secara otomatis!"
            else:
                automation_status = f"\n\n⚠️ File `{filename}` berhasil disimpan lokal, tetapi gagal push otomatis ke GitHub."
        else:
            automation_status = "\n\nℹ️ Catatan: Tidak ada blok kode terdeteksi untuk disimpan otomatis."

        final_output = reply_text + automation_status
        if len(final_output) > 4000:
            final_output = final_output[:3900] + "\n\n*(Teks dipotong karena terlalu panjang)*"

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=final_output
        )

    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"❌ Terjadi kesalahan sistem: {str(e)}"
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 AI Agent Berjalan di Termux... Siap Menerima Perintah Otomatis.")
    app.run_polling()
    
