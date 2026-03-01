import os
import requests
import time

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")

def get_ai_response(user_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချိုသာယဉ်ကျေးတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ မြန်မာလိုပဲ ဖြေပေးပါ။\nUser: {user_input}"}]
        }]
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        res = r.json()
        if 'candidates' in res:
            return res['candidates'][0]['content']['parts'][0]['text']
        else:
            # API ကနေ ဘာ Error ပြန်လဲဆိုတာကို Bot က ပြောပြပါလိမ့်မယ်
            error_msg = res.get('error', {}).get('message', 'Unknown Error')
            return f"AI Error: {error_msg}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def main():
    last_update_id = 0
    print("Amara Bot is Starting...")
    while True:
        try:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            response = requests.get(tg_url, timeout=35).json()
            if "result" in response:
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        answer = get_ai_response(update["message"]["text"])
                        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(send_url, json={"chat_id": chat_id, "text": answer}, timeout=15)
        except:
            time.sleep(5)

if __name__ == '__main__':
    main()
