import os
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")

# Render Error မတက်အောင် Port ဖွင့်ပေးထားခြင်း
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), HealthCheckHandler)
    server.serve_forever()

def get_ai_response(user_input):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={KEY}"
    payload = {"contents": [{"parts": [{"text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချိုသာယဉ်ကျေးတဲ့ မြန်မာမိန်းကလေး AI တစ်ဦးဖြစ်ပါတယ်။ မြန်မာလိုပဲ ဖြေပေးပါ။\nUser: {user_input}"}]}]}
    try:
        r = requests.post(url, json=payload, timeout=20)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ခေတ္တလိုင်းမကောင်းလို့ပါရှင်။"

def main():
    # Health check server ကို Background မှာ မောင်းထားခြင်း
    threading.Thread(target=run_health_check, daemon=True).start()
    
    last_update_id = 0
    print("Amara Bot is Starting on Render...")
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
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": answer})
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
