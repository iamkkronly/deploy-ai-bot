from fastapi import FastAPI, Request
import telebot
import os
import requests

app = FastAPI()

# Load environment variables (no hardcoded keys)
TELEGRAM_BOT_TOKEN = os.environ["7388278300:AAHUM2fmyBTi9fzw3AfAgJQnycVgNwkyn9M"]
GEMINI_API_KEY = os.environ["AIzaSyA7a8YLdL_qWxoXqumA2zcW7_SKskRMSRE"]

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Webhook Endpoint
@app.post("/webhook")
async def webhook(request: Request):
    update = telebot.types.Update.de_json(await request.json())
    bot.process_new_updates([update])
    return {"message": "ok"}

# Root Endpoint (for testing)
@app.get("/")
def index():
    return {"message": "Telegram bot is running"}

# Example Handlers (customize as needed)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I'm your bot. How can I assist you today?")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)  # Replace with your Gemini API logic