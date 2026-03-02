import telebot
import os
import requests
from flask import Flask # flask ကို သုံးပြီး port ဖွင့်ပါမည်

# ... (အရင်ရှိပြီးသား get_amara_response နှင့် handle_message ကုဒ်များ)

server = Flask(__name__)

@server.route("/")
def webhook():
    return "Amara Bot is Running!", 200

if __name__ == "__main__":
    # Telegram Bot ကို Background မှာ Run ခိုင်းခြင်း
    import threading
    threading.Thread(target=bot.infinity_polling).start()
    
    # Render အတွက် Port ဖွင့်ပေးခြင်း
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
