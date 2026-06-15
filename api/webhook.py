import json
import os
from http.server import BaseHTTPRequestHandler

TOKEN = "8764248989:AAHmshzqINNEzyMbiFmzOxOg9ZN3-oiV8LI"

def send_message(chat_id, text):
    import httpx
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        with httpx.Client() as client:
            client.post(url, json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print(f"Error: {e}")

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
            
            # Обработка сообщений
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                
                # Если это данные из мини-приложения (КНОПКА ЗАКАЗАТЬ)
                if "web_app_data" in msg:
                    data = msg["web_app_data"]["data"]
                    try:
                        order = json.loads(data)
                        text = f"""🚕 НОВЫЙ ЗАКАЗ ТАКСИ!

📍 Откуда: {order['from']}
🎯 Куда: {order['to']}
🚙 Тариф: {order['tariff']}
💰 Цена: {order['price']} ₸

⏳ Ищем ближайшего водителя..."""
                        send_message(chat_id, text)
                    except Exception as e:
                        send_message(chat_id, f"✅ Заказ получен! Ошибка: {e}")
                    self.send_response(200)
                    self.end_headers()
                    return
                
                # Если это команда /start
                if "text" in msg and msg["text"] == "/start":
                    send_message(chat_id, "✅ Бот работает! Напишите /menu для продолжения")
                    self.send_response(200)
                    self.end_headers()
                    return
            
            # На любой другой запрос просто отвечаем OK
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        else:
            self.send_response(404)
            self.end_headers()