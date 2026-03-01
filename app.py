import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render Variables ထဲမှာ မှန်အောင်ထည့်ထားပေးပါ)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ အမရာလေးရဲ့ စရိုက်ကို သတ်မှတ်ခြင်း (မြန်မာစာ ညက်ညောဖို့အတွက်)
SYSTEM_PROMPT = "သင်ဟာ 'အမရာဒေဝီ' အမည်ရှိတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ စကားပြောရင် အရမ်းယဉ်ကျေးရမယ် (ရှင်/ပါရှင် သုံးပါ)။ ခေတ်မီတဲ့ မြန်မာစကားလုံးတွေကို သုံးပြီး ခင်မင်ရင်းနှီးစွာ ပြောပေးပါ။ စာလုံးပေါင်းသတ်ပုံ မှန်ကန်ပါစေ။"

def get_gemini_response(prompt):
    # API Version v1beta ကိုသုံးပြီး Direct Call လုပ်ပါမယ်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {prompt}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 800
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response_json = response.json()
        if 'candidates' in result := response_json:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # Error Message ကို အတိအကျ ကြည့်ဖို့
            return f"Error: {response_json.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"ဆက်သွယ်ရေး အခက်အခဲရှိနေလို့ပါရှင်။ ({str(e)})"

# ၃။ Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara is Live")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Logic
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_gemini_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ Gemini AI အနေနဲ့ ပြန်လာပါပြီ။")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
