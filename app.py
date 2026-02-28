import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# ၁။ Page Config
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# ၂။ API Key & Model Setup
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 404 error မတက်အောင် models/ ပါအောင် ထည့်ထားပါတယ်
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    st.error("API Key မတွေ့ပါ။ Manage app > Settings > Secrets မှာ ထည့်ပေးပါ။")

# ၃။ Audio Function
def speak(text):
    try:
        tts = gTTS(text=text, lang='my')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# ၄။ Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ၅။ Chat Input
if prompt := st.chat_input("အမရာဒေဝီကို တစ်ခုခု မေးပါ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # အမရာဒေဝီရဲ့ ကိုယ်ရည်ကိုယ်သွေး
            instruction = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။"
            full_prompt = f"{instruction}\nမေးခွန်း: {prompt}"
            
            response = model.generate_content(full_prompt)
            reply = response.text
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            speak(reply)
        except Exception as e:
            st.error(f"အမရာ စကားပြောဖို့ ခေတ္တအခက်အခဲရှိနေတယ်ရှင်။ (Error: {e})")
