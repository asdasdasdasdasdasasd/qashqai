import requests
from bs4 import BeautifulSoup
import time
import telebot
from flask import Flask
from threading import Thread

# 🔧 CONFIGURATION
URL = "https://www.mobile.bg/obiavi/avtomobili-dzhipove/nissan/qashqai/dizelov/ot-2016/do-2021/namira-se-v-balgariya?price1=10000&currency=EUR&km=200000"
TELEGRAM_TOKEN = "7787577003:AAF3mZyznwx6go_sCUZF_ljQk8IDpnOkbTM"
CHAT_ID = "1660290308"

# ✅ Initialize Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ✅ Store already-seen listings
seen_ads = set()

def check_new_listings():
    global seen_ads

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.select("div.listing a.lnk")  # Each ad entry

    new_ads = []

    for link in listings:
        href = link.get("href")
        title = link.get_text(strip=True)

        if href and href.startswith("/obiava"):
            full_url = "https://www.mobile.bg" + href

            if full_url not in seen_ads:
                seen_ads.add(full_url)
                new_ads.append((title, full_url))

    for title, url in new_ads:
        msg = f"🚗 <b>New Qashqai Listing</b>\n<a href=\"{url}\">{title}</a>"
        bot.send_message(CHAT_ID, msg, parse_mode="HTML")

# 🔁 Start the scraper in a separate thread
def start_scraper():
    print("🚀 Qashqai monitor started...")
    while True:
        try:
            check_new_listings()
            print("✅ Checked for new listings.")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(60)  # Check every 60 seconds

# ✅ Flask server to keep Render & UptimeRobot happy
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# 🔁 Run both web server and scraping loop
Thread(target=start_scraper).start()
Thread(target=run_web).start()
