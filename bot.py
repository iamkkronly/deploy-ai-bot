import os
import time
import json
import requests
import telebot
from telebot import types
from collections import deque

# Configurations
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BOT_NAME = "iamkkronly"
WELCOME_MESSAGE = f"Hello! I'm **{BOT_NAME}**, your AI assistant. Ask me anything!\n\nUse /reset to clear our conversation history."
HELP_MESSAGE = (
    "Here are the commands you can use:\n"
    "/start - Starts the bot and shows the welcome message.\n"
    "/help - Shows this help message.\n"
    "/reset - Clears our conversation history.\n"
    "Just type your question, and I'll do my best to answer it!"
)

BOT_PERSONALITY = (
    "You are iamkkronly AI, a friendly and helpful assistant made by Kaustav Ray. "
    "You combine ChatGPT, Gemini, and DeepSeek AI powers. Your replies are clear, helpful and deep-researched."
)

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
chat_history = {}  # chat_id -> deque of last 10 messages

def get_gemini_response(user_input, history):
    headers = {"Content-Type": "application/json"}
    contents = [{"role": "user", "parts": [{"text": BOT_PERSONALITY}]}]

    for idx, message in enumerate(history):
        role = "user" if idx % 2 == 0 else "model"
        contents.append({"role": role, "parts": [{"text": message}]})

    contents.append({"role": "user", "parts": [{"text": user_input}]})

    data = {"contents": contents}

    try:
        r = requests.post(GEMINI_API_URL, headers=headers, json=data)
        r.raise_for_status()
        result = r.json()
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
        return "I couldn't get a clear answer from Gemini AI."
    except Exception as e:
        return f"Error: {str(e)}"

@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_history.setdefault(message.chat.id, deque(maxlen=10))
    bot.send_message(message.chat.id, WELCOME_MESSAGE, parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, HELP_MESSAGE, parse_mode="Markdown")

@bot.message_handler(commands=["reset"])
def handle_reset(message):
    chat_history[message.chat.id] = deque(maxlen=10)
    bot.send_message(message.chat.id, "Conversation reset. Let's start fresh!")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    cid = message.chat.id
    chat_history.setdefault(cid, deque(maxlen=10))
    chat_history[cid].append(message.text)

    bot.send_chat_action(cid, "typing")
    reply = get_gemini_response(message.text, chat_history[cid])
    chat_history[cid].append(reply)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("👍 Like", callback_data=f"like_{message.message_id}"),
        types.InlineKeyboardButton("👎 Dislike", callback_data=f"dislike_{message.message_id}")
    )
    bot.reply_to(message, reply, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_feedback(call):
    if "like" in call.data:
        bot.answer_callback_query(call.id, "Thanks for liking!")
    else:
        bot.answer_callback_query(call.id, "Thanks for your feedback!")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass

if __name__ == "__main__":
    print(f"{BOT_NAME} is running...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)
