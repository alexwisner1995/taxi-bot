import json
import os
import re
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN", "8764248989:AAHmshzqINNEzyMbiFmzOxOg9ZN3-oiV8LI")

# Хранилище пользователей (временное, при перезапуске сбросится)
users = {}

def send_message(chat_id, text, reply_markup=None):
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        with httpx.Client() as client:
            client.post(url, json=payload)
    except Exception as e:
        print(f"Error: {e}")

def send_callback(chat_id, text, callback_id):
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    try:
        with httpx.Client() as client:
            client.post(url, json={"callback_query_id": callback_id, "text": text})
    except Exception as e:
        print(f"Error: {e}")

# Клавиатура выбора языка
def lang_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🇰🇿 Қазақша", "callback_data": "lang_kz"}],
            [{"text": "🇷🇺 Русский", "callback_data": "lang_ru"}],
            [{"text": "🇬🇧 English", "callback_data": "lang_en"}]
        ]
    }

# Клавиатура выбора роли
def role_keyboard(lang):
    texts = {
        "kz": {"passenger": "🚖 Жолаушы", "driver": "🚙 Жүргізуші"},
        "ru": {"passenger": "🚖 Пассажир", "driver": "🚙 Водитель"},
        "en": {"passenger": "🚖 Passenger", "driver": "🚙 Driver"}
    }
    return {
        "inline_keyboard": [
            [{"text": texts[lang]["passenger"], "callback_data": "role_passenger"}],
            [{"text": texts[lang]["driver"], "callback_data": "role_driver"}]
        ]
    }

# Главное меню пассажира
def passenger_menu(lang):
    texts = {
        "kz": "🚖 Такси шақыру",
        "ru": "🚖 Заказать такси",
        "en": "🚖 Order taxi"
    }
    return {
        "keyboard": [[{"text": texts[lang]}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/webhook":
            self.send_response(405)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Taxi Bot is running!")

    def do_POST(self):
        if self.path == "/api/webhook":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            update = json.loads(body)
            
            # Обработка команды /start
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                
                if text == "/start":
                    users[chat_id] = {"step": "language"}
                    send_message(chat_id, "Тіл таңдаңыз / Выберите язык / Choose language:", lang_keyboard())
                    self.send_response(200)
                    self.end_headers()
                    return
                
                # Главное меню пассажира
                if text in ["🚖 Такси шақыру", "🚖 Заказать такси", "🚖 Order taxi"]:
                    send_message(chat_id, "🚕 Открываем форму заказа... (скоро добавим мини-приложение)")
                    self.send_response(200)
                    self.end_headers()
                    return
            
            # Обработка callback-запросов (кнопки)
            if "callback_query" in update:
                query = update["callback_query"]
                chat_id = query["message"]["chat"]["id"]
                data = query["data"]
                callback_id = query["id"]
                
                if data.startswith("lang_"):
                    lang = data.split("_")[1]
                    users[chat_id] = {"step": "role", "lang": lang}
                    send_message(chat_id, "Кімсіз? / Кто вы? / Who are you?", role_keyboard(lang))
                    send_callback(chat_id, "✅ Тіл таңдалды", callback_id)
                
                elif data.startswith("role_"):
                    role = data.split("_")[1]
                    lang = users.get(chat_id, {}).get("lang", "ru")
                    if role == "passenger":
                        send_message(chat_id, "✅ Сіз жолаушы ретінде тіркелдіңіз!\n✅ Вы зарегистрированы как пассажир!\n✅ You are registered as a passenger!", passenger_menu(lang))
                    else:
                        send_message(chat_id, "🚖 Режим водителя\n\nКогда будете готовы выезжать, нажмите /online")
                    send_callback(chat_id, "✅ Роль таңдалды", callback_id)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()