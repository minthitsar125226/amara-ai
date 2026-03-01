import os
import threading
import requests
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render Variables ထဲမှာ နာမည်မှန်အောင် စစ်ပေးပါ)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ Gemini API Call (Direct Standard Call)
def get_gemini_response(prompt):
    # v1 version နဲ့ gemini-1.5-flash ကို အသေ သုံးပါမယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{
                "text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိတဲ့ ချိုသာယဉ်ကျေးတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ မြန်မာလိုပဲ ဖြေပေးပါ။\n\nUser: {prompt}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "အမရာ ခေတ္တ အနားယူနေလို့ပါရှင်။ ခဏနေမှ ထပ်မေးပေးမလားဟင်။"
    except:
        return "ချိတ်ဆက်မှု အခက်အခဲလေး ရှိနေလို့ပါရှင်။"

# ၃။ Render Health Check (Port Error မတက်အောင်)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara is Live")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Logic (Version 20+ Standard)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ အသင့်ရှိနေပါပြီ။")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if not user_input: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_gemini_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    # Health Check ကို Background မှာ မောင်းမယ်
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Telegram Bot ကို Version 20+ ပုံစံနဲ့ မောင်းမယ်
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("Bot is starting...")
    application.run_polling()
