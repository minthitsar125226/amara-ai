import os
import telebot
import requests
import time

# Key များကို ယူခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def get_amara_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemini-flash-1.5",
        "messages": [{"role": "system", "content": "မင်းနာမည်က အမရာဒေဝီပါ။"}, {"role": "user", "content": user_input}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "ခဏလေးနော်၊ အမရာ အလုပ်ရှုပ်နေလို့ပါ။"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_amara_response(message.text)
    bot.reply_to(message, reply)

# Conflict Error ကို ကျော်လွှားရန်အတွက် Webhook ကို ဖျက်ခြင်း
if __name__ == "__main__":
    print("Deleting old webhooks...")
    bot.remove_webhook()
    time.sleep(1) # ခဏနားပါ
    print("Amara Devi is starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
