import json
import os
import re
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN", "8764248989:AAHmshzqINNEzyMbiFmzOxOg9ZN3-oiV8LI")

# Хранилище пользователей (временное)
users = {}

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        with httpx.Client() as client:
            client.post(url, json=payload)
    except Exception as e:
        print(f"Send error: {e}")

def send_callback(chat_id, text, callback_id):
    """Ответ на callback запрос"""
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    try:
        with httpx.Client() as client:
            client.post(url, json={"callback_query_id": callback_id, "text": text})
    except Exception as e:
        print(f"Callback error: {e}")

def send_webapp_response(chat_id, webapp_url):
    """Отправка мини-приложения"""
    keyboard = {
        "inline_keyboard": [[{
            "text": "🚕 Открыть такси",
            "web_app": {"url": webapp_url}
        }]]
    }
    send_message(chat_id, "🚕 Нажмите кнопку, чтобы заказать такси:", keyboard)

def lang_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🇰🇿 Қазақша", "callback_data": "lang_kz"}],
            [{"text": "🇷🇺 Русский", "callback_data": "lang_ru"}],
            [{"text": "🇬🇧 English", "callback_data": "lang_en"}]
        ]
    }

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

def handle_order(chat_id, data):
    """Обработка заказа из мини-приложения"""
    import httpx
    try:
        order = json.loads(data)
        if order.get("action") == "order":
            text = f"""🚕 **НОВЫЙ ЗАКАЗ ТАКСИ**

📍 **Откуда:** {order['from']}
🎯 **Куда:** {order['to']}
🚙 **Тариф:** {order['tariff']}
💰 **Цена:** {order['price']} ₸

⏳ Ищем ближайшего водителя..."""
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            with httpx.Client() as client:
                client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
            return True
    except Exception as e:
        print(f"Order error: {e}")
    return False

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
            
            # ========== ОБЫЧНЫЕ СООБЩЕНИЯ ==========
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                
                # Команда /start
                if "text" in msg and msg["text"] == "/start":
                    users[chat_id] = {"step": "language"}
                    send_message(chat_id, "Тіл таңдаңыз / Выберите язык / Choose language:", lang_keyboard())
                    self.send_response(200)
                    self.end_headers()
                    return
                
                # Текстовые сообщения (кнопки главного меню)
                if "text" in msg and msg["text"] in ["🚖 Такси шақыру", "🚖 Заказать такси", "🚖 Order taxi"]:
                    webapp_url = "https://taxi-bot-five.vercel.app/static/index.html"
                    send_webapp_response(chat_id, webapp_url)
                    self.send_response(200)
                    self.end_headers()
                    return
                
                # Данные из мини-приложения
                if "web_app_data" in msg:
                    data = msg["web_app_data"]["data"]
                    handle_order(chat_id, data)
                    self.send_response(200)
                    self.end_headers()
                    return
            
            # ========== CALLBACK ЗАПРОСЫ (кнопки) ==========
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
                        send_message(chat_id, "✅ Вы зарегистрированы как пассажир!", passenger_menu(lang))
                    else:
                        send_message(chat_id, "🚖 Режим водителя\n\nКогда будете готовы, нажмите /online")
                    send_callback(chat_id, "✅ Роль выбрана", callback_id)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()