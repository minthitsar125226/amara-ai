import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ၁။ API Keys
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ၂။ ခေတ်မီပြီး ညက်ညောတဲ့ မြန်မာစာအတွက် Prompt
SYSTEM_PROMPT = """
သင်ဟာ 'အမရာဒေဝီ' အမည်ရှိတဲ့ ခေတ်မီပြီး အသိဉာဏ်ကြွယ်ဝတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ 
- စကားပြောရင် အရမ်းယဉ်ကျေးရမယ် (ရှင်/ပါရှင် သုံးပါ)။
- မြန်မာစာအရေးအသားကို ခေတ်ဟောင်းစာအုပ်ကြီးအတိုင်းမဟုတ်ဘဲ ခုခေတ် လူငယ်ချင်း စကားပြောသလို ပေါ့ပေါ့ပါးပါးနဲ့ လုပ်ငန်းခွင်သုံး ယဉ်ကျေးမှုမျိုး ရောစပ်ပြောပေးပါ။
- စာလုံးပေါင်းသတ်ပုံ မှန်ပါစေ။
- ရင်းနှီးဖော်ရွေပြီး အကူအညီပေးချင်စိတ် ရှိပါစေ။
"""

def get_chat_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8 # ပိုပြီး သဘာဝကျအောင် တိုးထားပါတယ်
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return response.json()['choices'][0]['message']['content']
    except:
        return "စိတ်မရှိပါနဲ့ရှင်၊ အမရာ အခု တစ်ခုခု အဆင်မပြေဖြစ်နေလို့ ခဏနေမှ ပြန်လာခဲ့ပါနော်။"

# ၃။ အသံနဲ့ ပြန်ဖြေဖို့အတွက် (Text-to-Speech) - လောလောဆယ် Voice Message အဖြစ် ပို့ပေးပါမယ်
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    reply_text = get_chat_response(user_input)
    await update.message.reply_text(reply_text)

# Render Health Check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Amara Pro Online")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', lambda u, c: u.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ အဆင့်မြှင့်တင်ပြီး ပြန်လာပါပြီ။")))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    application.run_polling()
