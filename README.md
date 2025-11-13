AI Automation Projects — Dishant Makawana

A collection of practical automation systems, AI-powered assistants, and workflow tools built using Python, vector search, APIs, and real-time logic.
Each project here demonstrates how automation can simplify operations across business, IT, HR, and support processes.

About Me

I’m Dishant Makawana, an AI Automation Engineer from Ahmedabad, India.
I build applied automation — real systems that reduce workload, streamline communication, and transform manual tasks into intelligent workflows.

Areas of focus:

AI Assistants & Knowledge Bots

Document Search (RAG)

Business workflow automation

Data orchestration and reporting

Telegram/Slack automation

Low-code / no-code integrations

Completed Projects

Below is a structured, clean table listing all completed automation projects.

Project	Description	Technologies
AI Knowledge Assistant	Slack-based internal knowledge bot using local vector search (FAISS). Reads PDFs, CSVs & TXT files and answers HR/IT/policy questions. Includes a local Sandbox for evaluation, retraining, and testing.	Python, Flask, Slack Bolt, FAISS, MiniLM, LangChain, Pandas
Telegram Forwarder Bot	Automatically forwards specific messages between Telegram groups. Useful for signal channels, monitoring, and broadcast groups.	Python, Telethon
AI Reporter Bot	Pulls real-time data from APIs (CoinGecko, FakeStore), formats reports, and sends AI-style insights to Telegram.	Python, Telethon, Requests
Business Workflow Orchestrator	Merges sales, leads, and attendance data into unified daily KPI summaries with automated insights delivered to Telegram.	Python, Pandas, Telethon
Featured Project
AI Knowledge Assistant (Slack RAG System)

A complete corporate-style internal knowledge bot designed for HR, IT, Admin, Finance, and Operations teams.

Key Features

Local, private document embedding using FAISS

Uses SentenceTransformers (MiniLM) for high-quality vector retrieval

Answers are filtered, focused, and reliable

Supports contact detail enrichment (contacts.csv)

Runs fully offline (no paid LLM required)

Complete Sandbox Framework for evaluation:

Batch question testing

Automatic similarity scoring

Retraining pipeline

Logs & performance tracking

Why It Works So Well

No hallucination: responses only come from embedded documents

Highly stable: deterministic, consistent answers

Modular: can be extended with an LLM rewriter later

Production-friendly: clean retrieval + filtered outputs

Technology Stack

Languages & Libraries

Python 3.x

Flask / FastAPI

Slack Bolt SDK

Telethon

AI & Retrieval

FAISS Vector Store

SentenceTransformers (all-MiniLM-L6-v2)

LangChain Community Tools

Data & Utilities

Pandas

Requests

dotenv

Ngrok (for Slack event tunneling)

Philosophy Behind This Repository

Build systems, not demos

Prioritize real-world workflows over theoretical examples

Focus on clarity, modularity, and testability

Develop automation that any business team can use immediately

Ensure solutions are fast, stable, and secure

Author

Dishant Makawana
AI Automation Engineer
Ahmedabad, India
LinkedIn: www.linkedin.com/in/dishant-makawana-4b849b137

Support

If these projects inspire you or help your work:
Consider starring ⭐ this repository.
More projects and upgrades are added regularly.
