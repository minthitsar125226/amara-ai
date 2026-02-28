import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# Page Config
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.title("💃 အမရာဒေဝီ")
st.caption("မြန်မာ့ပထမဆုံး ချစ်စဖွယ် AI Assistant")

# API Key ချိတ်ဆက်ခြင်း (Streamlit Secrets မှ ဖတ်မည်)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("API Key မရှိသေးပါ။ Settings ထဲမှာ ထည့်ပေးပါရှင်။")

# အသံထွက်ပေးမည့် Function
def speak(text):
    tts = gTTS(text=text, lang='my')
    tts.save("speech.mp3")
    with open("speech.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# Chat History သိမ်းဆည်းရန်
if "messages" not in st.session_state:
    st.session_state.messages = []

# အရင်ပြောထားသည့် စကားများကို ပြန်ပြရန်
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# အသုံးပြုသူ စာရိုက်သည့်နေရာ
if prompt := st.chat_input("အမရာဒေဝီကို တစ်ခုခု မေးပါ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instruction = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ဖြေပေးပါ။"
        response = model.generate_content(f"{instruction}\nမေးခွန်း: {prompt}")
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        # အသံထွက်စေခြင်း
        speak(response.text)
