
import os, requests, time, threading
from bs4 import BeautifulSoup
from http.server import HTTPServer, BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")
KEY = os.environ.get("GEMINI_API_KEY")
# ဂိမ်းရလဒ်စာမျက်နှာ Link (ဥပမာ - ဘောလုံး သို့မဟုတ် အခြားဂိမ်း)
TARGET_URL = "https://www.myan88.co/m/home" 

def scrape_myan88():
    try:
        # ဆိုဒ်က Bot လို့ မသိအောင် Browser တစ်ခုလို ဟန်ဆောင်ခြင်း
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return f"ဆိုဒ်က ဝင်ခွင့်မပြုပါ (Error: {response.status_code})"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # မှတ်ချက် - ဒီနေရာမှာ ဆိုဒ်ရဲ့ class နာမည်တွေအပေါ် မူတည်ပြီး ဒေတာဆွဲရမှာပါ
        # Myan88 က JavaScript သုံးထားရင် ဒီနည်းလမ်းနဲ့ ဒေတာပါလာမှာ မဟုတ်ပါဘူး
        all_text = soup.get_text()
        # နောက်ဆုံးရလဒ်အချို့ကို စမ်းသပ်ထုတ်ယူခြင်း
        important_data = all_text.strip()[:500] 
        return important_data
        
    except Exception as e:
        return f"ချိတ်ဆက်မှု အခက်အခဲ: {str(e)}"

def get_prediction(data):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={KEY}"
    prompt = (
        f"ဒီအချက်အလက်တွေက Myan88 ဂိမ်းဆိုဒ်က ရလဒ်တွေဖြစ်ပါတယ်။ {data} \n"
        "ဒီ Pattern တွေကို ကြည့်ပြီး နောက်တစ်ကြိမ်မှာ ဘာဖြစ်နိုင်လဲဆိုတာကို "
        "သင်္ချာနည်းအရ ဖြစ်နိုင်ခြေ တွက်ချက်ပြီး မြန်မာလို အကြံပြုပေးပါ။"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI ခန့်မှန်းချက် ထုတ်လို့မရသေးပါရှင်။"

# --- Telegram Bot Main Loop ---
# (အရင်ပေးထားတဲ့ main function ကို ဒီ functions တွေနဲ့ ချိတ်ဆက်သုံးနိုင်ပါတယ်)
