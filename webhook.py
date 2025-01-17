import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import types
from main import bot

class Handler(BaseHTTPRequestHandler):
    server_version = 'WebhookHandler/1.0'

    def do_GET(self):
    time.sleep(1.5)
    # Defina a URL do webhook diretamente
    bot.set_webhook(url='https://dark-assistente-ia-telegram.vercel.app/webhook')
    self.send_response(200)
    self.end_headers()

    def do_POST(self):
        cl = int(self.headers['Content-Length'])
        post_data = self.rfile.read(cl)
        body = json.loads(post_data.decode())

        bot.process_new_updates([types.Update.de_json(body)])

        self.send_response(204)
        self.end_headers()

def run(server_class=HTTPServer, handler_class=Handler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
