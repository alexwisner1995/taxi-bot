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
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Taxi Bot is running!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        update = json.loads(body)
        
        print(f"Update: {update}")  # Для логов Vercel
        
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            send_message(chat_id, "✅ Бот работает! Ваше сообщение получено.")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())