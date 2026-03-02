import os
import telebot
import requests

# Render Environment ကနေ Key တွေကို ယူခြင်း
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
        "model": "google/gemini-flash-1.5", # သို့မဟုတ် "openrouter/auto"
        "messages": [
            {"role": "system", "content": "မင်းနာမည်က အမရာဒေဝီပါ။ မြန်မာလိုပဲ ပြန်ဖြေပေးပါ။"},
            {"role": "user", "content": user_input}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        # အဖြေကို သေချာထုတ်ယူခြင်း
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        else:
            return f"OpenRouter က အဖြေမပေးနိုင်ဘူးဖြစ်နေတယ်ဗျ။ Error: {response_json.get('error', {}).get('message', 'Unknown')}"
    except Exception as e:
        return f"Error တစ်ခုခု တက်သွားတယ်: {str(e)}"

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    reply = get_amara_response(message.text)
    bot.reply_to(message, reply)

# Bot ကို စတင်နှိုးခြင်း
bot.infinity_polling()
