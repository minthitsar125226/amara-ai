import os
import telebot
import requests

# ပတ်ဝန်းကျင် ကိန်းရှင်များမှ Data ယူခြင်း
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def get_amara_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemini-flash-1.5", # OpenRouter ထဲက model နာမည်
        "messages": [
            {"role": "system", "content": "မင်းဟာ မြန်မာလို ကျွမ်းကျင်စွာ ပြောနိုင်တဲ့ အမရာဒေဝီ အမည်ရှိ AI တစ်ဦး ဖြစ်တယ်။ ဂိမ်းခန့်မှန်းချက်တွေကိုလည်း ကူညီပေးနိုင်ရမယ်။"},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "ခေတ္တလိုင်းမကောင်းလို့ပါ၊ ခဏနေမှ ပြန်ကြိုးစားကြည့်ပေးပါနော်။"

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    reply = get_amara_response(message.text)
    bot.reply_to(message, reply)

bot.infinity_polling()
