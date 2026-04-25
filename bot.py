import requests
from bs4 import BeautifulSoup
import time
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
send_telegram("🔥 TEST: bot ancora vivo")

# 🎯 OBIETTIVI DA MONITORARE
TARGETS = [
    {
        "name": "Tamron 70-300",
        "url": "https://www.rcefoto.com/scheda-prodotto/tamron-70-300mm-f4-5-6-3-di-iii-rxd/",
        "max_price": 300
    }
]

SEEN_FILE = "seen.json"


def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def get_offers(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)

        if "/prodotto/" in href and text:
            full_link = "https://www.rcefoto.com" + href

            # prova a estrarre prezzo
            price = None
            for part in text.split():
                if "€" in part:
                    try:
                        price = int(part.replace("€", "").replace(".", ""))
                    except:
                        pass

            offers.append({
                "title": text,
                "link": full_link,
                "price": price
            })

    return offers


def send_telegram(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )


def format_message(target_name, offer):
    price = offer["price"]

    emoji = "🔥" if price and price < 250 else "⚡"

    msg = (
        f"{emoji} NUOVA OFFERTA\n\n"
        f"📸 {target_name}\n"
        f"🛍 {offer['title']}\n\n"
        f"💰 {price if price else 'N/D'}€\n\n"
        f"🔗 {offer['link']}"
    )

    return msg

seen = load_seen()
last_notify = time.time()

while True:
    try:
        offers = get_offers(TARGETS[0]["url"])

        found_new = False

        for offer in offers:
            key = offer["link"]

            if offer["price"] and offer["price"] > TARGETS[0]["max_price"]:
                continue

            if key not in seen:
                seen.add(key)
                found_new = True

                msg = format_message(TARGETS[0]["name"], offer)
                send_telegram(msg)

        save_seen(seen)

        if time.time() - last_notify >= 600:
            if not found_new:
                send_telegram("⏳ Ancora niente nuove offerte...")
            last_notify = time.time()

        time.sleep(120)

    except Exception as e:
        print("Errore:", e)
        time.sleep(30)
