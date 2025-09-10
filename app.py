from flask import Flask, request
import requests
import json
import os
from datetime import date

app = Flask(__name__)

# === تنظیمات
TOKEN = "7901146555:AAGmTO4dSmWZyeMLm3r5n_7Is6Cz8mY7Xjk"
URL = f"https://api.telegram.org/bot{TOKEN}/"

# === ارسال پیام
def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# === بارگذاری فایل JSON
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === مسیر وبهوک
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update or "message" not in update:
        return "no message"

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "").strip()

    # بارگذاری فایل‌ها
    words = load_json("words.json", [])
    users = load_json("users.json", {})

    if str(chat_id) not in users:
        users[str(chat_id)] = {
            "learned": [],
            "lastDate": "",
            "todayWord": None
        }

    user = users[str(chat_id)]
    today = str(date.today())

    # انتخاب کلمه جدید اگر امروز اولین بار هست
    if user["lastDate"] != today:
        available_words = [w for w in words if w not in user["learned"]]
        if available_words:
            user["todayWord"] = available_words[0]  # میشه تصادفی هم گذاشت
            user["learned"].append(user["todayWord"])
            user["lastDate"] = today
        else:
            user["todayWord"] = "🎉 همه کلمات رو یاد گرفتی!"

    # پاسخ دادن
    if text.lower() in ["/start", "شروع"]:
        send_message(chat_id, "سلام 👋 آماده‌ایم برای یادگیری روزانه!")
    else:
        send_message(chat_id, f"کلمه امروزت: {user['todayWord']}")

    # ذخیره اطلاعات
    save_json("users.json", users)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)