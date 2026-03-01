import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys (Render Variables ထဲမှာ နာမည်မှန်အောင် စစ်ပေးပါ)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def get_gemini_response(prompt):
    # v1 version ကို သုံးပြီး Model နာမည်ကို အတိအကျ ခေါ်ပါမယ်
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # Google Gemini API ရဲ့ Standard JSON Format
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
        
        # အဖြေကို ဆွဲထုတ်ခြင်း
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # ဘာ Error တက်လဲဆိုတာ Telegram မှာ တန်းမြင်ရအောင် ပြပါမယ်
            error_msg = result.get('error', {}).get('message', 'Unknown Error')
            return f"Error ပါရှင်: {error_msg}"
            
    except Exception as e:
        return f"ချိတ်ဆက်မှု အဆင်မပြေပါရှင်။ ({str(e)})"

# ၂။ Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၃။ Telegram Bot Logic
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_gemini_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ အသင့်ရှိနေပါပြီ။")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
