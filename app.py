import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render Variables ထဲက ဖတ်မယ်)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ AI Response Logic (Version နှင့် Model အကုန်လုံးကို လှည့်စမ်းပေးမည့်စနစ်)
def get_chat_response(prompt):
    # စမ်းသပ်မည့် Endpoint ပေါင်းစပ်မှုများ
    test_configs = [
        {"ver": "v1beta", "model": "gemini-1.5-flash"},
        {"ver": "v1", "model": "gemini-pro"},
        {"ver": "v1beta", "model": "gemini-pro"},
        {"ver": "v1", "model": "gemini-1.5-flash"}
    ]
    
    for config in test_configs:
        v = config["ver"]
        m = config["model"]
        url = f"https://generativelanguage.googleapis.com/{v}/models/{m}:generateContent?key={GEMINI_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မြန်မာမိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။\nUser: {prompt}"}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            if 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
            
    return "အမရာ အခု စကားပြောဖို့ အားနည်းနေလို့ပါရှင်။ ခဏနေမှ ပြန်လာခဲ့ပေးပါဦးနော်။"

# ၃။ Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ Telegram မှာ အဆင့်သင့်ရှိနေပါပြီ။")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_chat_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
