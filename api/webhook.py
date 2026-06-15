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
        print(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Taxi Bot is running!")

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        update = json.loads(body)

        if "message" in update and "web_app_data" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            data = update["message"]["web_app_data"]["data"]
            try:
                order = json.loads(data)
                text = f"🚕 Заказ: {order['to']}, {order['tariff']}, {order['price']} ₸"
                send_message(chat_id, text)
            except:
                send_message(chat_id, "Заказ получен!")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())