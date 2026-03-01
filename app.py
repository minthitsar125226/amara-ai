import os
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")

# Render Port Error မတက်အောင် Dummy Server ဖွင့်ခြင်း
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Alive")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheck)
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
    # Server ကို Background မှာ မောင်းထားမယ်
    threading.Thread(target=run_server, daemon=True).start()
    
    last_id = 0
    print("Bot is Running...")
    while True:
        try:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id + 1}&timeout=30"
            res = requests.get(tg_url, timeout=35).json()
            if "result" in res:
                for up in res["result"]:
                    last_id = up["update_id"]
                    if "message" in up and "text" in up["message"]:
                        chat_id = up["message"]["chat"]["id"]
                        reply = get_ai_response(up["message"]["text"])
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
        except:
            time.sleep(5)

if __name__ == '__main__':
    main()
