import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# ၁။ Page Setup
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# ၂။ API Configuration
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 404 Error မတက်အောင် model နာမည်ကို အသေချာဆုံးပုံစံ ပြောင်းထားပါတယ်
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
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
            instruction = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။"
            response = model.generate_content(f"{instruction}\nမေးခွန်း: {prompt}")
            reply = response.text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            speak(reply)
        except Exception as e:
            st.error(f"အမရာ စကားပြောဖို့ ခဏလေး အခက်အခဲဖြစ်သွားတယ်ရှင်။ (Error: {e})")
