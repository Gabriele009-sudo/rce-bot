import requests
from bs4 import BeautifulSoup
import time
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.rcefoto.com/scheda-prodotto/tamron-70-300mm-f4-5-6-3-di-iii-rxd/"

DATA_FILE = "seen.json"
MAX_PRICE = 380  # cambia se vuoi


def get_products():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    products = []

    cards = soup.find_all("a", href=True)

    for card in cards:
        href = card["href"]

        if "/prodotto/" in href:
            text = card.get_text(" ", strip=True)

            price = None
            for part in text.split():
                if "€" in part:
                    try:
                        price = int(part.replace("€", "").replace(".", ""))
                    except:
                        pass

            if price:
                products.append({
                    "name": text,
                    "price": price,
                    "link": "https://www.rcefoto.com" + href
                })

    return products


def send_message(text):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
    )


def load_seen():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_seen(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


seen = load_seen()

if not seen:
    seen = get_products()
    save_seen(seen)

while True:
    try:
        current = get_products()

        new_items = [
            p for p in current
            if p not in seen and p["price"] <= MAX_PRICE
        ]

        for item in new_items:
            send_message(
                f" <b>NUOVA OFFERTA!</b>\n\n"
                f"{item['name']}\n"
                f" {item['price']}€\n\n"
                f"<a href='{item['link']}'>Apri prodotto</a>"
            )

        seen = current
        save_seen(seen)

        time.sleep(300)

    except Exception as e:
        print("Errore:", e)
        time.sleep(60)