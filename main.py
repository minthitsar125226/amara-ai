import os
import telebot
import requests

# Render Environment ကနေ Key တွေကို သေချာဖတ်ခြင်း
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

def get_amara_response(user_input):
    # Key မရှိရင် Error ပြရန်
    if not OPENROUTER_KEY:
        return "OpenRouter Key မရှိသေးပါဘူးခင်ဗျာ။ Environment မှာ စစ်ပေးပါ။"
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY.strip()}", # strip() က space ပါရင် ဖြတ်ပေးပါတယ်
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemini-flash-1.5",
        "messages": [
            {"role": "system", "content": "မင်းနာမည်က အမရာဒေဝီပါ။ မြန်မာလိုပဲ ပြန်ဖြေပေးပါ။"},
            {"role": "user", "content": user_input}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        # API ကနေ Data ပြန်မလာတဲ့ TypeError ကို ဒီမှာ ကာကွယ်ထားပါတယ်
        if response_json and 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            error_msg = response_json.get('error', {}).get('message', 'Unknown API Error')
            return f"OpenRouter API မှာ ပြဿနာရှိနေပါတယ်- {error_msg}"
            
    except Exception as e:
        return f"စက်ပိုင်းဆိုင်ရာ ချို့ယွင်းချက်- {str(e)}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        reply = get_amara_response(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Bot Error: {e}")

# Bot ကို စတင်နှိုးခြင်း
if __name__ == "__main__":
    print("Amara Devi Bot is starting...")
    bot.infinity_polling()
