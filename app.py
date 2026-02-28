import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import base64

# ၁။ Page Config
st.set_page_config(page_title="အမရာဒေဝီ AI", page_icon="💃")
st.markdown("<h1 style='text-align: center;'>💃 အမရာဒေဝီ</h1>", unsafe_allow_html=True)

# ၂။ Smart Model Selection System
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # အလုပ်လုပ်နိုင်ခြေရှိတဲ့ Model စာရင်း
    available_models = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-pro'
    ]
    
    # အလုပ်လုပ်တဲ့ Model ကို အလိုအလျောက် ရှာဖွေခြင်း
    if "active_model" not in st.session_state:
        st.session_state.active_model = None
        for model_name in available_models:
            try:
                test_model = genai.GenerativeModel(model_name)
                # စမ်းသပ် စာရိုက်ကြည့်ခြင်း
                test_model.generate_content("test", generation_config={"max_output_tokens": 1})
                st.session_state.active_model = model_name
                break
            except:
                continue
                
    if st.session_state.active_model:
        model = genai.GenerativeModel(st.session_state.active_model)
    else:
        st.error("သင့် API Key နှင့် ကိုက်ညီသော Model ရှာမတွေ့ပါ။")
else:
    st.error("API Key မတွေ့ပါ။ Manage app > Settings > Secrets တွင် ထည့်ပေးပါ။")

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

# ၄။ Chat Logic
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
            st.error(f"အမရာ စကားပြောဖို့ အခက်အခဲရှိနေတယ်ရှင်။ (Error: {e})")
