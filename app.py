import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

orders = {}
next_order_id = 1


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if keyboard:
        data["reply_markup"] = {
            "inline_keyboard": keyboard
        }

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json=data,
        timeout=10
    )


def edit_message(chat_id, message_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if keyboard:
        data["reply_markup"] = {
            "inline_keyboard": keyboard
        }

    requests.post(
        f"{TELEGRAM_API}/editMessageText",
        json=data,
        timeout=10
    )


def order_text(order):
    return (
        f"📦 <b>İŞ #{order['id']:03d}</b>\n\n"
        f"🏢 📍 {order['description']}\n"
        f"📌 <b>Durum:</b> {order['status']}\n"
        f"👤 <b>Personel:</b> {order['worker'] or 'Henüz alınmadı'}"
    )


@app.route("/")
def home():
    return "Takım Yıldızı İş Takip Botu çalışıyor."


@app.route("/webhook", methods=["POST"])
def webhook():
    global next_order_id

    update = request.get_json(silent=True) or {}

    # Normal mesaj = yeni sipariş
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if not text:
            return "ok"

        if text == "/start":
            send_message(
                chat_id,
                "📦 <b>TAKIM YILDIZI İŞ TAKİP</b>\n\n"
                "Yeni iş oluşturmak için müşteri ve varış yerini yaz.\n\n"
                "Örnek:\n"
                "<b>Deniz Rulman Çankırı</b>"
            )
            return "ok"

        order_id = next_order_id
        next_order_id += 1

        order = {
            "id": order_id,
            "description": text,
            "status": "🔴 ALINACAK",
            "worker": None
        }

        orders[order_id] = order

        keyboard = [[{
            "text": "🚗 İŞİ ALIYORUM",
            "callback_data": f"claim:{order_id}"
        }]]

        send_message(
            chat_id,
            order_text(order),
            keyboard
        )

    # Buton işlemleri
    elif "callback_query" in update:
        query =
