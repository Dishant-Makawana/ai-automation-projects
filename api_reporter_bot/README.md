# 🧠 AI-Driven API Reporter Bot

A small but powerful automation that fetches live data from **multiple free APIs**, generates **AI-style insights**, and posts a neat report to Telegram on a schedule.  
Built to behave like an internal, corporate-grade tool — using only free resources.

---

## 🚀 What It Does

- Pulls **Bitcoin price & 24h change** from CoinGecko  
- Simulates **orders & sales** using FakeStore API (free demo data)  
- Produces **AI-style insights** (Market + Store)  
- Sends a formatted report to a **Telegram group** automatically  
- Uses a secure **.env** file (no hard-coded secrets)  
- Adjustable update interval (seconds or minutes)

---

## 🧰 Tech Stack

| Component | Purpose |
|------------|----------|
| **Python** | Core language |
| **Telethon** | Telegram API client |
| **Requests** | Fetch data from public APIs |
| **python-dotenv** | Securely load environment variables |
| **time / random** | Scheduling + mock AI summaries |

---

## 📁 Project Structure
api_reporter_bot/
├─ api_reporter.py # main script
├─ .gitignore # hides .env, sessions, caches
├─ README.md # documentation
└─ report_demo.mp4 # (optional) short demo clip

---

## 🔐 Environment Variables

Create a file named `.env` inside your `api_reporter_bot/` folder:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
SESSION_NAME=dishant_api_reporter
DEST_CHAT=-100xxxxxxxxxx
🔑 Get your API credentials from my.telegram.org
DEST_CHAT = Telegram group ID where the bot posts.

⚙️ Setup & Run
1️⃣ Install dependencies:
pip install requests python-dotenv telethon

2️⃣ Run the bot: 
python api_reporter.py

3️⃣ Adjust update interval
Open the script and edit:

UPDATE_INTERVAL = 1800   # 30 minutes (e.g., 60 = 1min, 3600 = 1hr)


🧾 Example Output:

📊 **Dishant’s AI Reporter Bot**
🕒 08 Nov 2025 | 14:47:57

💰 BTC Price: $102,209
📈 24h Change: 0.8% (positive)

🛍️ Orders (FakeStore): 7
🧾 Total Sales (est): $4,20

🧠 **AI Insights:**
• Market Insight: steady and balanced
• Store Insight: consistent demand across products
----------------------------------
⏱️ Report updates every 30 min ⚙️



🧩 Troubleshooting
If no message appears in Telegram:

Check your .env values

Ensure your Telegram account (or bot) is in the target group

Confirm the DEST_CHAT ID begins with -100

If rate-limited → increase UPDATE_INTERVAL



🗺️ Roadmap / Future Enhancements
Real AI summaries (OpenAI / local LLM integration)

Google Sheets or Slack output options

Multi-symbol and multi-API support

Error logging, retry logic & uptime tracking


🧑‍💻 Author
Dishant Makawana
AI Automation & Business Systems Builder
📍 Ahmedabad, Gujarat, India

⚙️ Part of my AI Automation Series — showing how small, smart systems can transform daily operations.
