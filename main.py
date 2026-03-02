import telebot
import os
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def get_amara_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "google/gemini-2.0-flash-001", # ဒီနာမည်က အရေးကြီးဆုံးပါ
        "messages": [
            {"role": "system", "content": "မင်းနာမည်က အမရာဒေဝီပါ။ ချိုချိုသာသာ ပြန်ဖြေပေးပါ။"},
            {"role": "user", "content": user_input}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except:
        return "အမရာ စဉ်းစားနေလို့ပါရှင်။"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_amara_response(message.text)
    bot.reply_to(message, reply)

if __name__ == "__main__":
    bot.infinity_polling()
