import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render Variables ထဲက ဖတ်မယ်)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ Gemini API Call (v1 Stable Version ကို တိုက်ရိုက်ခေါ်ခြင်း)
def get_chat_response(prompt):
    # v1beta အစား v1 ကို သုံးကြည့်ပါမယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မြန်မာမိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။\nUser: {prompt}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        result = response.json()
        
        # အဖြေရရင် ပြန်ပေးမယ်
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # API က ပြန်လာတဲ့ Error message အစစ်ကို ထုတ်ပြမယ်
            error_info = result.get('error', {}).get('message', 'Unknown API Error')
            return f"Error ပါရှင် (API Message: {error_info})"
            
    except Exception as e:
        return f"ချိတ်ဆက်မှု Error တက်နေပါတယ်ရှင် (System: {str(e)})"

# ၃။ Render Health Check (Port Binding အတွက်)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara is online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ Telegram မှာ အသင့်ရှိနေပါပြီ။ တစ်ခုခု မေးမြန်းနိုင်ပါတယ်ရှင်။")

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
