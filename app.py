import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render မှာ ဒီ ၂ ခုလုံး ထည့်ထားပေးပါ)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

SYSTEM_PROMPT = "သင်ဟာ အမရာဒေဝီ အမည်ရှိတဲ့ ခေတ်မီပြီး အသိဉာဏ်ကြွယ်ဝတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ စကားပြောရင် ယဉ်ကျေးရမယ် (ရှင်/ပါရှင် သုံးပါ)။ ခေတ်မီတဲ့ စကားလုံးတွေနဲ့ ရင်းနှီးဖော်ရွေစွာ ပြောပေးပါ။"

# ၂။ Gemini ကို အရင်စမ်းမယ်
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    data = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\nUser: {prompt}"}]}]}
    response = requests.post(url, json=data, timeout=10)
    return response.json()['candidates'][0]['content']['parts'][0]['text']

# ၃။ Gemini မရရင် Groq ကို သုံးမယ်
def get_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data, timeout=10)
    return response.json()['choices'][0]['message']['content']

# ၄။ Main Logic (Backup စနစ်)
def get_final_response(prompt):
    try:
        return get_gemini_response(prompt)
    except:
        try:
            return get_groq_response(prompt)
        except:
            return "စိတ်မရှိပါနဲ့ရှင်၊ အမရာ ခဏလေး စဉ်းစားရခက်နေလို့ နောက်တစ်ခါ ပြန်မေးပေးပါလားဟင်။"

# Render Health Check & Telegram Setup
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara Smart Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_final_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ အဆင့်မြှင့်တင်ပြီး ပြန်လာပါပြီ။")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
