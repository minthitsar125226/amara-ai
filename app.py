
import os, requests, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")

# ၁။ Render ပေါ်မှာ Bot အမြဲတမ်း Live ဖြစ်နေစေဖို့
class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"AI Toolkit Online")

def start_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Health)
    server.serve_forever()

# ၂။ Gemini AI ဦးနှောက် (Smart Assistant Mode)
def ask_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={KEY}"
    # ဖုန်းမှာဖတ်ရလွယ်အောင် တိုတိုနဲ့လိုရင်းပဲ ဖြေခိုင်းထားပါတယ်
    prompt = f"သင်ဟာ အလွန်တော်တဲ့ မြန်မာ AI လက်ထောက်တစ်ဦးပါ။ User ကို တိုတိုနဲ့ လိုရင်းပဲ ဖြေပေးပါ။\n\nUser: {text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=30)
        res = r.json()
        if 'candidates' in res:
            return res['candidates'][0]['content']['parts'][0]['text']
        return f"AI System Error: {res.get('error', {}).get('message', 'Key စစ်ပါ')}"
    except Exception as e:
        return f"လိုင်းမကောင်းလို့ပါရှင်- {str(e)}"

# ၃။ Telegram Bot Main Logic
def main():
    threading.Thread(target=start_server, daemon=True).start()
    last_id = 0
    print("AI Toolkit is Ready on your Phone!")
    
    while True:
        try:
            tg_url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=30"
            r = requests.get(tg_url, timeout=40).json()
            for up in r.get("result", []):
                last_id = up["update_id"]
                if "message" in up and "text" in up["message"]:
                    chat_id = up["message"]["chat"]["id"]
                    # AI အဖြေကို ရယူပြီး ပြန်ပို့ခြင်း
                    reply = ask_gemini(up["message"]["text"])
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
        except:
            time.sleep(5)

if __name__ == '__main__':
    main()
