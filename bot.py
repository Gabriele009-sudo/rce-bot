import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.rcefoto.com/scheda-prodotto/tamron-70-300mm-f4-5-6-3-di-iii-rxd/"

seen = set()


def get_offers():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    offers = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)

        if "/prodotto/" in href and text:
            full_link = "https://www.rcefoto.com" + href

            offers.append((text, full_link))

    return offers


def send_telegram(message):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False
        }
    )


print("🔥 BOT RCE AVVIATO")

while True:
    try:
        offers = get_offers()

        for title, link in offers:
            if link not in seen:
                seen.add(link)

                send_telegram(
                    f"📸 NUOVO ANNUNCIO RCE!\n\n"
                    f"{title}\n\n"
                    f"{link}"
                )

        time.sleep(120)

    except Exception as e:
        print("Errore:", e)
        time.sleep(30)
