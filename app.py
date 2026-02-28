import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# ၁။ Page Setup
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# ၂။ API Configuration & Smart Model Selection
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Model နာမည် အမျိုးမျိုးကို စမ်းသပ်ရန် စာရင်းသွင်းထားခြင်း
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash-8b',
        'gemini-1.5-pro'
    ]
    
    # အလုပ်လုပ်တဲ့ Model တစ်ခုကို အလိုအလျောက် ရွေးချယ်ခြင်း
    if "model_name" not in st.session_state:
        st.session_state.model_name = models_to_try[0]
        for m in models_to_try:
            try:
                genai.GenerativeModel(m).generate_content("Hi")
                st.session_state.model_name = m
                break
            except:
                continue
    
    model = genai.GenerativeModel(st.session_state.model_name)
else:
    st.error("API Key မတွေ့ပါ။ Manage app > Settings > Secrets ကို စစ်ပေးပါ။")

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

# ၄။ Chat System
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("အမရာဒေဝီကို တစ်ခုခု မေးပါ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            role = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။"
            response = model.generate_content(f"{role}\n{prompt}")
            reply = response.text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            speak(reply)
        except Exception as e:
            st.error(f"အမရာ စကားပြောဖို့ အခက်အခဲရှိနေတယ်ရှင်။ (Error: {e})")
