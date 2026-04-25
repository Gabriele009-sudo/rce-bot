import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

r = requests.get(url, params={
    "chat_id": CHAT_ID,
    "text": "🔥 TEST BOT: se vedi questo, Telegram funziona!"
})

print(r.status_code)
print(r.text)
