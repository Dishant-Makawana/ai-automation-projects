🚀 Trending Topic Research Automation (n8n Workflow)
📌 Project Overview

Trending Topic Research Automation Using n8n Workflow

🧩 Problem Statement
Manually researching trending topics across platforms like YouTube, Twitter, Reddit, and news sites is inefficient and time-consuming. This limits marketing teams from consistently generating fresh, data-driven content ideas aligned with real-time audience interests.

🎯 Objective
To automate the discovery and synthesis of trending content topics from multiple digital sources using an n8n workflow.
This system empowers marketing agencies and businesses with a consistent, scalable, and data-driven process for generating strategic content ideas — reducing manual effort and increasing relevance.

📚 Background
Content ideation is critical for timely engagement. But manual research typically takes 3–4 hours per session and often misses emerging trends.
By combining n8n automation + AI analysis, this workflow removes bottlenecks and ensures a continuous pipeline of valuable ideas.

This automation benefits:

- Marketing strategists
- Content creators
- Agencies
- Business owners needing quick insights

⚙️ Core Components
- Trigger
- Weekly cron-based schedule
- Fully automated, no manual involvement
- Integrations
- YouTube Data API v3 – trending video metadata
- Twitter API (via twitterapi.io or OpenAI-generated mock)
- NewsAPI – trending articles
- Reddit API – active discussions
- OpenAI GPT-4o-mini – AI-powered analysis
- Google Sheets API – structured output storage
- Trello (optional) – content idea task creation

Logic & Processing:
- Random keyword selected from 130+ curated business topics
- Parallel multi-API data retrieval

AI analyzes:
- audience interest patterns
- signals
- relevance
- themes

Aggregates everything into 10 strategic content ideas with:

title
- short description
- format
- priority
- rationale
- Output

Appends generated ideas to Google Sheets (“Content Ideas” tab)

Optional:
- Creates Trello cards for execution
- Sends updates to dashboards

🌟 Bonus Capabilities
Trello CRM pipeline automation
Looker Studio real-time dashboards
Strict fallback logic + error-proofing
Easily extendable — add more APIs or keywords anytime

✅ Validation & Evaluation

This workflow demonstrates:
Efficiency
Reduces manual research workload by 3+ hours per session.
Output Quality
Consistently produces 10 high-quality, data-driven ideas per run.
Reliability
Includes structured error handling + fallback sources.
Integration Clarity
Clean node structure with secure API authentication.

Scalability:
Extendable with minimal changes.

Innovation:
AI synthesizes insights beyond raw data scraping.

📦 Folder Contains

- n8n workflow (.json export)
- Screenshots:
- Google Sheet sample
- Trello sample
- Looker Studio dashboard
- README.txt

🔗 Shared Access
Google Sheet (View Only)
https://docs.google.com/spreadsheets/d/1kBhLUor994zfFfoFg54xL0kJ2PVK5t2EJGev5k5ChqU/edit?usp=sharing

Looker Studio Dashboard (View Only)
https://lookerstudio.google.com/reporting/e1419103-7399-4078-8cce-1e43d7551a60

Video walkthrough:
https://drive.google.com/file/d/1AWOmcpuy3NJk1R5Go5FfKFPHRWYlGCHU/view?usp=sharing

📝 Notes
All sensitive data has been removed.
Only workflow logic, node structure, and processing steps are included.
Credentials are not exported from n8n and remain secure.

✍️ Author

Dishant Makawana
AI Automation Builder • Logical Thinker • Fast Executor • Business-Oriented Systems Designer
