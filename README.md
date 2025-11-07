# Telegram Forwarder Bot 🤖

A lightweight automation that listens to messages from one Telegram group and instantly forwards them to another — built with **Python**, **Telethon**, and **dotenv**.

---

## 🚀 Features
- Auto-forwards every new message from a source group to a destination group.  
- Secure configuration using `.env` (no hard-coded keys).  
- Can run 24/7 on any system or VPS.  
- Clean, minimal, and beginner-friendly.

---

## 🧠 How It Works
1. The bot logs in through Telegram’s API (using your API ID & hash).  
2. It watches the **SOURCE_CHAT** for new messages.  
3. On every new message, it sends the same content to **DEST_CHAT**.  

---

## ⚙️ Requirements
```bash
pip install telethon python-dotenv
