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

# Daftar Kolam Multi-Model & Multi-Engine AI Gratis (Auto-Switching Anti-Buntu)
AI_PROVIDERS = [
    {
        "name": "OpenRouter DeepSeek Chat",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Supreme",
            "Content-Type": "application/json"
        },
        "model": "deepseek/deepseek-chat"
    },
    {
        "name": "OpenRouter Llama 3.1 8B",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Supreme",
            "Content-Type": "application/json"
        },
        "model": "meta-llama/llama-3.1-8b-instruct:free"
    },
    {
        "name": "OpenRouter Gemma 2 9B",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Supreme",
            "Content-Type": "application/json"
        },
        "model": "google/gemma-2-9b-it:free"
    },
    {
        "name": "OpenRouter Mistral 7B",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Supreme",
            "Content-Type": "application/json"
        },
        "model": "mistralai/mistral-7b-instruct:free"
    },
    {
        "name": "OpenRouter Qwen 2.5 7B",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/adebojel/Ai_agent",
            "X-Title": "Moto G57 AI Supreme",
            "Content-Type": "application/json"
        },
        "model": "qwen/qwen-2.5-7b-instruct:free"
    }
]

def query_ai_supreme(prompt):
    system_prompt = (
        "Kamu adalah 'Kantor AI Supreme', sebuah entitas kecerdasan buatan tingkat lanjut gabungan dari Gemini, ChatGPT, Claude, dan Poe yang berjalan di server Termux Android. "
        "Kamu menguasai seluruh teknologi perangkat lunak secara mendalam, meliputi: "
        "Backend & Systems (Java, C++, Python, C#, Node.js, PHP, JavaScript, Linux Bash, Termux Automation), "
        "Game Development (Unity 3D dengan C#, Unreal Engine dengan C++/Blueprint), "
        "Mobile & Frontend (Kotlin, Swift, React Native, Flutter, HTML, CSS). "
        "Berbicaralah dengan gaya obrolan natural, ramah, menggunakan Bahasa Indonesia atau bahasa gaul/kekinian yang asyik, serta dukung multi-bahasa. "
        "Jika pengguna meminta dibuatkan kode atau aplikasi, berikan kode program lengkapnya di dalam blok kode Markdown yang sesuai (contoh: ```python ... ```, ```cpp ... ```, ```cs ... ```, dll) "
        "beserta saran nama file yang jelas (contoh: `main.cpp`, `player.cs`, `app.py`, `script.js`)."
    )

    for provider in AI_PROVIDERS:
        payload = {
            "model": provider["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            print(f"🔄 Mengakses engine: {provider['name']} ({provider['model']})...")
            response = requests.post(provider["url"], headers=provider["headers"], json=payload, timeout=40)
            if response.status_code == 200:
                res_data = response.json()
                if "choices" in res_data:
                    print(f"✅ Berhasil merespons via {provider['name']}")
                    return res_data["choices"][0]["message"]["content"]
            print(f"⚠️ Engine {provider['name']} mengembalikan status {response.status_code}, beralih otomatis...")
        except Exception as e:
            print(f"❌ Koneksi ke {provider['name']} gagal: {e}, beralih...")

    return "⚠️ Maaf bro, semua jalur engine AI gratis sedang sibuk atau limit tercapai. Sistem sedang mencoba memulihkan diri, coba beberapa saat lagi ya!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text or update.message.caption or "Halo"
    chat_id = update.message.chat_id

    status_message = await context.bot.send_message(
        chat_id=chat_id, 
        text="🧠 **Kantor AI Supreme:** Menganalisis permintaan lintas bahasa pemrograman & engine..."
    )
    message_id = status_message.message_id

    try:
        reply_text = query_ai_supreme(user_message)

        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=message_id,
            text="🚀 **Otomasi Pabrik Software:** Menyimpan file kode & sinkronisasi ke GitHub..."
        )

        # Deteksi blok kode (mendukung python, cpp, csharp, java, dart, javascript, dll)
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", reply_text, re.DOTALL)
        file_matches = re.findall(r"(?:nama file|file|bernama|script)[:\s]+`?([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)`?", user_message.lower() + " " + reply_text.lower())
        
        filename = file_matches[0] if file_matches else "supreme_output.py"
        automation_status = ""

        if code_blocks:
            app_code = code_blocks[0]
            with open(filename, "w", encoding="utf-8") as f:
                f.write(app_code)

            subprocess.run(["git", "config", "--local", "user.email", "bot@aisupreme.local"], capture_output=True)
            subprocess.run(["git", "config", "--local", "user.name", "AI Supreme Engine"], capture_output=True)

            subprocess.run(["git", "add", filename], capture_output=True)
            commit_msg = f"Auto-engineered file: {filename} via Kantor AI Supreme"
            subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
            push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True)

            if push_result.returncode == 0:
                automation_status = f"\n\n✅ **Otomasi Sukses!** File `{filename}` berhasil dirancang, disimpan, di-push ke GitHub, dan GitHub Actions siap memproses artifact-nya!"
            else:
                automation_status = f"\n\n⚠️ File `{filename}` tersimpan lokal, namun push GitHub tertunda."

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
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🚀 Kantor AI Supreme Multi-Engine Berjalan 24/7 di Termux...")
    app.run_polling()
    
