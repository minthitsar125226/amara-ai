import os, requests, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# API Settings
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def get_gemini_response(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    data = {"contents": [{"parts": [{"text": f"သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချိုသာတဲ့ မြန်မာမိန်းကလေး AI ဖြစ်ပါတယ်။\nUser: {text}"}]}]}
    try:
        r = requests.post(url, json=data, timeout=10).json()
        return r['candidates'][0]['content']['parts'][0]['text']
    except: return "ခဏလေးနော်၊ အမရာ စဉ်းစားနေလို့ပါရှင်။"

def handle_bot():
    last_update_id = 0
    while True:
        try:
            updates = requests.get(f"{BASE_URL}/getUpdates?offset={last_update_id + 1}", timeout=10).json()
            if "result" in updates:
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        user_text = update["message"]["text"]
                        requests.post(f"{BASE_URL}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})
                        reply = get_gemini_response(user_text)
                        requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": reply})
        except: pass
        time.sleep(1)

# Render Port Binding
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"Amara Active")

if __name__ == '__main__':
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), H).serve_forever(), daemon=True).start()
    handle_bot()
