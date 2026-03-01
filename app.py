import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# ၁။ API Keys ထည့်ပါ
TELEGRAM_TOKEN = "8741702013:AAF_2mu1VH_B3NpFnpFlg_51uvCT51mhVQg"
GEMINI_KEY = "AIzaSyDtkx31Tg0-AoD--wcHcKiMgUfY2pjBILs"

# Gemini Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါရှင်၊ အမရာဒေဝီ နိုးထလာပါပြီ။ တစ်ခုခု မေးလို့ရပါပြီရှင်။")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        instruction = "သင်ဟာ အမရာဒေဝီ အမည်ရှိ ချစ်စဖွယ် မိန်းကလေး AI ဖြစ်ပါတယ်။ မြန်မာလိုပဲ ချိုချိုသာသာ ဖြေပေးပါ။"
        response = model.generate_content(f"{instruction}\n{user_input}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"အမရာ စကားပြောဖို့ အခက်အခဲရှိနေတယ်ရှင်။ Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    application.run_polling()
