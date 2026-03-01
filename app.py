import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64
import os

# Page Setup
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# API Key - Render ရဲ့ Environment Variable ကနေ ဖတ်မယ်
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Model ကို အလုပ်လုပ်ဆုံးဖြစ်တဲ့ gemini-1.5-flash-8b သုံးထားပါတယ်
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
else:
    st.error("API Key မတွေ့ပါ။ Render Settings > Environment Variables မှာ ထည့်ပေးပါ။")

def speak(text):
    try:
        tts = gTTS(text=text, lang='my')
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

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
            st.error(f"Error: {e}")
