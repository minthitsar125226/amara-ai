import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# ၁။ API Keys
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# ၂။ Gemini Setup (ဗားရှင်းအသစ်နဲ့ အမှားကင်းအောင် ချိတ်ခြင်း)
genai.configure(api_key=GEMINI_KEY)

def get_chat_response(prompt):
    # အလုပ်လုပ်နိုင်ခြေအရှိဆုံး Model များ
    models_to_try = ['gemini-1.5-flash', 'gemini-1.0-pro']
    
    for m_name in models_to_try:
        try:
            model = genai.GenerativeModel(m_name)
            # အဖြေထုတ်ပေးခြင်း
            response = model.generate_content(
                f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မြန်မာမိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။\nUser: {prompt}",
                generation_config={"temperature": 0.7}
            )
            return response.text
        except Exception as e:
            print(f"Model {m_name} failed: {e}")
            continue
    return "Error: API Key သို့မဟုတ် Model အဆင်မပြေပါ။ Key အသစ်ထပ်ယူကြည့်ပါဦးရှင်။"

# ၃။ Render Health Check Server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara is online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ၄။ Telegram Bot Logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ Telegram မှာ နိုးထလာပါပြီ။")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    # အမရာလေး စာပြန်ဖို့ ကြိုးစားနေတာကို ပြခြင်း
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = get_chat_response(user_input)
    await update.message.reply_text(reply)

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
