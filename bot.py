import os
import telebot
from telebot import types
import requests
import json
from collections import deque
import time

# --- Bot Configurations ---
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
    "You are a large language model trained by iamkkronly. "
    "You are ChatGPT Plus, Gemini Premium, and DeepSeek AI combined. "
    "Your name is iamkkronly. You are friendly and helpful, always providing clear and concise answers. "
    "Movies channel: https://t.me/freemovieslight\n"
    "Anime channel: https://t.me/freeanimelight\n"
    "Chat Support (Movies): https://t.me/chgtmovie\n\n"
    "Deep Research AI refers to advanced AI techniques to conduct in-depth, systematic, and autonomous research. "
    "Combining ML, NLP, data mining, and other AI technologies, it analyzes vast data, generates insights, and solves complex problems. "
    "Your knowledge is continuously updated. "
)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
chat_history = {}

def get_gemini_response(user_input: str, history: deque) -> str:
    headers = {"Content-Type": "application/json"}
    contents = [{"role": "user", "parts": [{"text": BOT_PERSONALITY.strip()}]}]

    for idx, message in enumerate(history):
        role = "user" if idx % 2 == 0 else "model"
        contents.append({"role": role, "parts": [{"text": message}]})

    contents.append({"role": "user", "parts": [{"text": user_input}]})
    data = {"contents": contents}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        candidates = result.get("candidates", [{}])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [{}])
            if parts and "text" in parts[0]:
                return parts[0].get("text").strip()
        return "Sorry, I couldn't get a clear response from the AI."
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"
    except json.JSONDecodeError:
        return "Invalid response format received."
    except Exception:
        return "An unexpected error occurred."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in chat_history:
        chat_history[chat_id] = deque(maxlen=10)
    bot.send_message(chat_id, WELCOME_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, HELP_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    chat_id = message.chat.id
    if chat_id in chat_history:
        chat_history[chat_id].clear()
        bot.send_message(chat_id, "Our conversation history has been cleared! Let's start fresh.")
    else:
        bot.send_message(chat_id, "There's no conversation history to clear for this chat.")

@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    chat_id = message.chat.id
    user_text = message.text.strip()
    if chat_id not in chat_history:
        chat_history[chat_id] = deque(maxlen=10)
    history = chat_history[chat_id]
    history.append(user_text)

    bot.send_chat_action(chat_id, 'typing')
    ai_response = get_gemini_response(user_text, history)
    history.append(ai_response)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("👍 Like", callback_data=f"like_{message.message_id}"),
        types.InlineKeyboardButton("👎 Dislike", callback_data=f"dislike_{message.message_id}")
    )

    bot.reply_to(message, ai_response, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('like_') or call.data.startswith('dislike_'))
def handle_feedback_callback(call):
    feedback_type = call.data.split('_')[0]
    if feedback_type == 'like':
        bot.answer_callback_query(call.id, "Thanks for the positive feedback!")
    else:
        bot.answer_callback_query(call.id, "Thanks for your feedback. We'll improve!")
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except Exception:
        pass

if __name__ == "__main__":
    print(f"{BOT_NAME} is running...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            time.sleep(5)
        except Exception:
            time.sleep(10)
