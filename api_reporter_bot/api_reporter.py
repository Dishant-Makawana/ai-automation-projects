from telethon import TelegramClient
from dotenv import load_dotenv
import os, requests, time, random
from datetime import datetime

# Load environment variables
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME")
DEST_CHAT = int(os.getenv("DEST_CHAT"))

# ========== Adjustable Settings ==========
UPDATE_INTERVAL = 60   # seconds; change to 3600 for hourly updates
# ========================================

client = TelegramClient(session_name, api_id, api_hash)

def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    data = requests.get(url).json()
    btc = data["bitcoin"]["usd"]
    change = round(data["bitcoin"]["usd_24h_change"], 2)
    return btc, change

def fetch_fake_store_data():
    try:
        orders = requests.get("https://fakestoreapi.com/carts").json()
        total_sales = 0
        for o in orders:
            for item in o["products"]:
                total_sales += item["quantity"] * 100  # dummy price
        return len(orders), total_sales
    except Exception as e:
        print("Error fetching store data:", e)
        return 0, 0

def generate_ai_summary(change, orders):
    # Mock AI summary (free, pseudo-AI style)
    market_trends = [
        "steady and balanced", "slightly bullish", "experiencing mild volatility",
        "under consolidation", "showing upward momentum", "cooling off a bit"
    ]
    store_trends = [
        "consistent demand across products", "moderate customer activity",
        "slightly slower order flow", "healthy buying sentiment",
        "higher engagement in cart activity"
    ]
    market_summary = random.choice(market_trends)
    store_summary = random.choice(store_trends)
    sentiment = "positive" if change > 0 else "negative" if change < 0 else "neutral"

    return market_summary, store_summary, sentiment

def build_report():
    btc, change = fetch_crypto_data()
    orders, total_sales = fetch_fake_store_data()
    market_summary, store_summary, sentiment = generate_ai_summary(change, orders)
    date = datetime.now().strftime("%d %b %Y | %H:%M:%S")

    report = (
        f"📊 **Dishant’s AI Reporter Bot**\n"
        f"🕒 {date}\n\n"
        f"💰 BTC Price: ${btc:,}\n"
        f"📈 24h Change: {change}% ({sentiment})\n\n"
        f"🛍️ Orders (FakeStore): {orders}\n"
        f"🧾 Total Sales (est): ${total_sales:,}\n\n"
        f"🧠 **AI Insights:**\n"
        f"• Market Insight: {market_summary}\n"
        f"• Store Insight: {store_summary}\n"
        f"----------------------------------\n"
        f"⏱️ Report updates every {UPDATE_INTERVAL // 60 if UPDATE_INTERVAL >= 60 else UPDATE_INTERVAL} "
        f"{'min' if UPDATE_INTERVAL >= 60 else 'sec'} ⚙️"
    )
    return report

async def send_report():
    msg = build_report()
    await client.send_message(DEST_CHAT, msg)
    print("Report sent at", datetime.now().strftime("%H:%M:%S"))

with client:
    while True:
        client.loop.run_until_complete(send_report())
        time.sleep(UPDATE_INTERVAL)
