import requests
from bs4 import BeautifulSoup
import time
import telebot
from flask import Flask
from threading import Thread

# 🔧 CONFIGURATION

TELEGRAM_TOKEN = "7787577003:AAF3mZyznwx6go_sCUZF_ljQk8IDpnOkbTM"
chat_id = -4939922320

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Store seen ads per site to avoid duplicates
seen_ads = {
    "mobilebg": set(),
    "carsbg": set(),
    "autobg": set(),
    "car24bg": set()
}

# URLs with your filters
URLS = {
    "mobilebg": "https://www.mobile.bg/obiavi/avtomobili-dzhipove/nissan/qashqai/dizelov/ot-2016/do-2021/namira-se-v-balgariya?price1=10000&currency=EUR&km=200000",
    "carsbg": "https://www.cars.bg/carslist.php?subm=1&add_search=1&typeoffer=1&brandId=60&models%5B%5D=1082&fuelId%5B%5D=2&priceTo=19000&conditions%5B%5D=4&conditions%5B%5D=1&yearFrom=2016&yearTo=2021",
    "autobg": "https://www.auto.bg/obiavi/avtomobili-dzhipove/nissan/qashqai/dizelov?price1=19000&year=2016&year1=2022",
    "car24bg": "https://www.car24.bg/obiavi/nissan/qashqai/dizelov/ot-2016?price=10000&price1=19000&km=200000"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_mobilebg():
    url = URLS["mobilebg"]
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    listings = soup.select("div.listing a.lnk")
    new_ads = []
    for link in listings:
        href = link.get("href")
        title = link.get_text(strip=True)
        if href and href.startswith("/obiava"):
            full_url = "https://www.mobile.bg" + href
            if full_url not in seen_ads["mobilebg"]:
                seen_ads["mobilebg"].add(full_url)
                new_ads.append((title, full_url))
    return new_ads

def scrape_carsbg():
    url = URLS["carsbg"]
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Cars.bg listings are inside div with class "list-item" and the link in h2 > a
    listings = soup.select("div.list-item h2 a")
    new_ads = []
    for link in listings:
        href = link.get("href")
        title = link.get_text(strip=True)
        if href and href.startswith("/"):
            full_url = "https://www.cars.bg" + href
            if full_url not in seen_ads["carsbg"]:
                seen_ads["carsbg"].add(full_url)
                new_ads.append((title, full_url))
    return new_ads

def scrape_autobg():
    url = URLS["autobg"]
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Auto.bg listings: links inside div with class "list" and 'a' tags with href starting "/obiava"
    listings = soup.select("div.list a[href^='/obiava']")
    new_ads = []
    for link in listings:
        href = link.get("href")
        title = link.get_text(strip=True)
        if href:
            full_url = "https://www.auto.bg" + href
            if full_url not in seen_ads["autobg"]:
                seen_ads["autobg"].add(full_url)
                new_ads.append((title, full_url))
    return new_ads

def scrape_car24bg():
    url = URLS["car24bg"]
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Car24.bg listings: links inside div with class "ad-title" > a
    listings = soup.select("div.ad-title a")
    new_ads = []
    for link in listings:
        href = link.get("href")
        title = link.get_text(strip=True)
        if href and href.startswith("/"):
            full_url = "https://www.car24.bg" + href
            if full_url not in seen_ads["car24bg"]:
                seen_ads["car24bg"].add(full_url)
                new_ads.append((title, full_url))
    return new_ads

def send_telegram(site_name, title, url):
    msg = f"🚗 <b>New Qashqai Listing on {site_name}</b>\n<a href=\"{url}\">{title}</a>"
    bot.send_message(CHAT_ID, msg, parse_mode="HTML")

def check_all_sites():
    # Mobile.bg
    for title, url in scrape_mobilebg():
        send_telegram("Mobile.bg", title, url)
    # Cars.bg
    for title, url in scrape_carsbg():
        send_telegram("Cars.bg", title, url)
    # Auto.bg
    for title, url in scrape_autobg():
        send_telegram("Auto.bg", title, url)
    # Car24.bg
    for title, url in scrape_car24bg():
        send_telegram("Car24.bg", title, url)

def start_scraper():
    print("🚀 Multi-site Qashqai monitor started...")
    while True:
        try:
            check_all_sites()
            print("✅ Checked all sites.")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(60)

# Flask server for uptime robot
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=start_scraper).start()
Thread(target=run_web).start()
