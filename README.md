🤖 AI Automation Projects by Dishant Makawana

A growing collection of intelligent automation systems, AI-powered bots, and workflow engines built using Python, APIs, vector search, and real-world business logic.
Each project here is designed with one purpose: simplify operations through smart automation.

👨‍💻 About Me

Hey! I’m Dishant Makawana, an AI Automation Engineer from Ahmedabad, India.
I build real business systems, not experiments — automations that actually reduce workload, simplify workflows, and provide intelligence where companies need it.

My approach is simple:

“Automation should feel like a superpower — not another tool.”

I specialise in:

Process automation (operations, HR, sales workflows)

AI assistants & chatbots (Slack/Telegram)

Data orchestration & reporting systems

API integrations & low-code/no-code logic

Real-time trading/market automation

📦 Completed Projects

Below are the finished, production-ready systems included in this repo:

Project	Description	Tech Used
AI Knowledge Assistant
	A Slack-based internal RAG assistant that reads company files (PDF/CSV/TXT), indexes them with FAISS, and answers HR/IT/policy questions instantly. Fully local, private, and fast. Comes with a testing Sandbox Dashboard for evaluation and retraining.	Python, Flask, Slack Bolt, FAISS, SentenceTransformers, LangChain, dotenv
Telegram Forwarder Bot
	Automatically forwards selected messages from one Telegram group to another — perfect for curated signal channels and team communication.	Python, Telethon, dotenv
AI Reporter Bot
	Pulls real-time data from APIs (CoinGecko, FakeStore), formats structured reports, and generates human-like AI insights before sending to Telegram.	Python, Requests, Telethon, dotenv
Business Workflow Orchestrator
	Merges and analyzes Sales, Leads, and Attendance data daily, then sends a unified KPI + insights summary automated to Telegram.	Python, Pandas, Telethon, dotenv
🚀 Featured Project
🧠 AI Knowledge Assistant + Sandbox Framework

A complete corporate-style internal knowledge system with:

✔️ Hybrid Slack Bot + Local RAG Model

Uses FAISS + MiniLM embeddings to store and retrieve knowledge

Answers questions based only on company documents — no hallucinations

Fully offline & private

✔️ Hard-Embedded & Stable Responses

We ensure consistent, deterministic answers by embedding refined reference answers into the vector store.

✔️ Intelligent Response Filtering

Instead of dumping full paragraphs, the bot returns:

only the relevant lines,

formatted cleanly,

with contact person lookup from a dedicated contacts.csv.

✔️ Custom Sandbox Environment

Built a separate testing dashboard to:

Collect answers for a batch of test questions

Compare them against reference answers

Generate evaluation reports

Automate retraining

Debug bots locally without Slack friction

This was designed to solve the biggest issue in corporate AI: quality control.

🧰 Core Tech Stack

Languages & Frameworks

Python 3.x

Flask / FastAPI

Slack Bolt

Telethon

AI & ML Tools

FAISS Vector Store

SentenceTransformers (all-MiniLM-L6-v2)

LangChain Community

Custom Retrieval Filters

Data & Automation

Pandas

Requests

dotenv

Ngrok (for Slack dev URLs)

🧠 Philosophy Behind This Repo

Keep automations practical

Build systems that mimic real corporate workflows

Design things that save hours, not minutes

Make everything modular for reuse

Showcase the real power of combining Python + AI + APIs

👨‍💻 Author

Dishant Makawana
AI Automation Engineer
📍 Ahmedabad, India
🔗 LinkedIn: www.linkedin.com/in/dishant-makawana-4b849b137

⭐ Support This Work

If you find these systems helpful or inspiring:
Star ⭐ the repo — it helps more than you think!
