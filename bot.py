import requests
from bs4 import BeautifulSoup
import time
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

print("🔥 BOT RCE MULTI-OBIETTIVO AVVIATO")

while True:
    try:
        for target in TARGETS:
            offers = get_offers(target["url"])

            for offer in offers:
                key = offer["link"]

                # filtro prezzo intelligente
                if offer["price"] and offer["price"] > target["max_price"]:
                    continue

                if key not in seen:
                    seen.add(key)

                    msg = format_message(target["name"], offer)
                    send_telegram(msg)

        save_seen(seen)

        time.sleep(120)

    except Exception as e:
        print("Errore:", e)
        time.sleep(30)
