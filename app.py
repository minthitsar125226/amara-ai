import os, requests, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def get_ai_response(prompt):
    # Gemini API သို့ တိုက်ရိုက်ချိတ်ဆက်ခြင်း
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={KEY}"
    data = {"contents": [{"parts": [{"text": f"သင်ဟာ အမရာဒေဝီ ဖြစ်ပါတယ်။ မြန်မာလိုဖြေပါ။\nUser: {prompt}"}]}]}
    try:
        r = requests.post(url, json=data, timeout=20)
        res = r.json()
        if 'candidates' in res:
            return res['candidates'][0]['content']['parts'][0]['text']
        # Error တက်ရင် ဘာကြောင့်လဲဆိုတာကို ပြန်ပြောခိုင်းမယ်
        return f"AI Error: {res.get('error', {}).get('message', 'Unknown Error')}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def main():
    # Render Port Error မတက်အောင် Dummy server ဖွင့်ခြင်း
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', port), Health).serve_forever(), daemon=True).start()
    
    last_id = 0
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=30").json()
            for up in r.get("result", []):
                last_id = up["update_id"]
                if "message" in up and "text" in up["message"]:
                    chat_id = up["message"]["chat"]["id"]
                    reply = get_ai_response(up["message"]["text"])
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": reply})
        except:
            time.sleep(5)

if __name__ == '__main__':
    main()
