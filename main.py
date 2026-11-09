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

# Daftar 9Router Multi-Model Fallback Gratis Terbaru (Otomatis Berpindah Jika Limit/Error)
FREE_MODELS = [
    "deepseek/deepseek-chat:free",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free"
]

def call_openrouter_multimodal(prompt, image_url=None):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
        "X-Title": "Moto G57 AI Supreme",
        "Content-Type": "application/json"
    }

    # Format pesan mendukung teks dan gambar (Multimodal ala Gemini/Claude)
    content_payload = [{"type": "text", "text": prompt}]
    if image_url:
        content_payload.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    for model in FREE_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah Asisten AI Supreme multiguna yang cerdas, ramah, dan adaptif. "
                        "Kamu menguasai berbagai bahasa termasuk Bahasa Indonesia, bahasa gaul/kekinian, dan multi-bahasa asing. "
                        "Jika diajak ngobrol santai, jadilah teman ngobrol yang asyik seperti ChatGPT, Claude, atau Gemini. "
                        "Jika pengguna meminta dibuatkan aplikasi/skrip, berikan kodenya secara lengkap di dalam blok kode Markdown (```python ... ```) "
                        "beserta nama file yang jelas (contoh: `catatan.py`)."
                    )
                },
                {"role": "user", "content": content_payload}
            ]
        }
        try:
            print(f"🔄 Mencoba model 9Router: {model}...")
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                res_data = response.json()
                if "choices" in res_data:
                    print(f"✅ Sukses menggunakan model: {model}")
                    return res_data["choices"][0]["message"]["content"]
            print(f"⚠️ Model {model} gagal (Status {response.status_code}), beralih otomatis...")
        except Exception as e:
            print(f"❌ Error pada model {model}: {e}, beralih...")
            
    return "⚠️ Maaf bro, semua jalur model 9Router gratis sedang sibuk atau habis kuotanya. Coba beberapa saat lagi ya!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text or update.message.caption or "Halo, bisa bantu saya?"
    chat_id = update.message.chat_id

    # Kirim status awal
    status_message = await context.bot.send_message(
        chat_id=chat_id, 
        text="🧠 **Kantor AI Supreme:** Menerima pesan & menganalisis permintaan..."
    )
    message_id = status_message.message_id

    image_url = None
    try:
        # Penanganan Multimodal (Foto / Gambar)
        if update.message.photo:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text="🖼️ **Multimodal:** Mendeteksi gambar, mengunduh dan menganalisis visual..."
            )
            photo_file = await update.message.photo[-1].get_file()
            image_url = photo_file.file_path

        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="⚡ **9Router:** Memproses kecerdasan AI (Chat & Otomasi)..."
        )

        # Panggil fungsi AI dengan sistem Multi-Model Fallback
        reply_text = call_openrouter_multimodal(user_message, image_url)

        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="🚀 **Otomasi:** Memeriksa blok kode & sinkronisasi ke GitHub..."
        )

        # Deteksi blok kode Python untuk otomatisasi rilis APK via GitHub Actions
        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", reply_text, re.DOTALL)
        file_matches = re.findall(r"(?:nama file|file|bernama)[:\s]+`?([a-zA-Z0-9_\-]+\.py)`?", user_message.lower() + " " + reply_text.lower())
        filename = file_matches[0] if file_matches else "app_generated.py"

        automation_status = ""
        if code_blocks:
            app_code = code_blocks[0]
            with open(filename, "w", encoding="utf-8") as f:
                f.write(app_code)

            subprocess.run(["git", "config", "--local", "user.email", "bot@aisupreme.local"], capture_output=True)
            subprocess.run(["git", "config", "--local", "user.name", "AI Supreme Bot"], capture_output=True)

            subprocess.run(["git", "add", filename], capture_output=True)
            commit_msg = f"Auto-generated app: {filename} via Telegram AI Supreme"
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
            push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True)

            if push_result.returncode == 0:
                automation_status = f"\n\n✅ **Otomasi Berhasil!** File `{filename}` tersimpan, ter-push ke GitHub, dan GitHub Actions sedang mem-build APK artifact secara otomatis!"
            else:
                automation_status = f"\n\n⚠️ File `{filename}` tersimpan lokal, namun gagal push otomatis ke GitHub."

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
            text=f"❌ Terjadi kesalahan sistem Supreme: {str(e)}"
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # Mendukung teks, foto, dan caption media
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & (~filters.COMMAND), handle_message))
    
    print("🚀 Kantor AI Supreme Berjalan di Termux... Siap Obrolan, Multimodal, & Otomasi 24/7.")
    app.run_polling()
    
