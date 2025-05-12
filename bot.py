from fastapi import FastAPI, Request
import telebot
import os
import requests
import json

app = FastAPI()

# Load environment variables (set these later in Vercel)
TELEGRAM_BOT_TOKEN = os.environ["7388278300:AAHUM2fmyBTi9fzw3AfAgJQnycVgNwkyn9M"]
GEMINI_API_KEY = os.environ["AIzaSyA7a8YLdL_qWxoXqumA2zcW7_SKskRMSRE"]

# Bot Personalization
BOT_NAME = "iamkkronly"
WELCOME_MESSAGE = f"Hello! I'm {BOT_NAME}, your AI assistant. Ask me anything!"
BOT_PERSONALITY = (
    "You are a large language model trained by iamkkronly. "
    "You are ChatGPT Plus, Gemini Premium, and DeepSeek AI combined. "
    "Your name is iamkkronly. You are friendly and helpful, always providing clear and concise answers. "
    "Movies channel: https://t.me/freemovieslight "
    "Anime channel: https://t.me/freeanimelight "
    "Chat Support (Movies): https://t.me/chgtmovie "
    "Your owner name is Kaustav Ray. "
    "You always reply after deep research. "
    "You are the fastest AI in the world."
)

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Google Gemini API URL
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Function to get AI response from Gemini
def get_gemini_response(user_input):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"{BOT_PERSONALITY}\n\nUser: {user_input}\n\nAI:"}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        candidates = result.get("candidates", [{}])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [{}])
            return parts[0].get("text", "No response found.")
        return "No response from AI."
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, WELCOME_MESSAGE)

# AI Response Handler
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    try:
        response = get_gemini_response(message.text)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "Sorry, I encountered an error. Please try again later.")

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