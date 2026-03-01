import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64
import os

# ၁။ Page Setup
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# ၂။ API Key & Smart Model Selector
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    
    # ရနိုင်သမျှ Model နာမည်အကုန်လုံးကို List ထဲထည့်ထားပါတယ်
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    # အလုပ်လုပ်တဲ့ Model တစ်ခုကို အလိုအလျောက် ရှာဖွေခြင်း
    if "active_model" not in st.session_state:
        st.session_state.active_model = None
        for m_name in models_to_try:
            try:
                temp_model = genai.GenerativeModel(m_name)
                # စမ်းသပ်စာရိုက်ကြည့်ပြီး အလုပ်လုပ်မှ ရွေးပါမယ်
                temp_model.generate_content("Hi", generation_config={"max_output_tokens": 1})
                st.session_state.active_model = m_name
                break
            except:
                continue
    
    if st.session_state.active_model:
        model = genai.GenerativeModel(st.session_state.active_model)
    else:
        st.error("API Key သို့မဟုတ် Model အဆင်မပြေဖြစ်နေပါသည်။ Key အသစ်ယူကြည့်ပါ။")
else:
    st.error("API Key မတွေ့ပါ။ Render Environment Variables ကို စစ်ပေးပါ။")

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
    except: pass

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
            st.error(f"Error: {e}")
