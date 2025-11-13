🧠 TCS Knowledge Assistant — Slack RAG Bot

A local, private, company-grade Knowledge Assistant that answers HR, IT, Admin, Finance, and Security questions directly inside Slack.

This project uses:  
FAISS vector database  
SentenceTransformer embeddings (MiniLM)  
Slack Bolt + Flask  
Custom retrieval filtering  
No external LLMs (zero cost, fully private)  
Ideal for enterprises needing fast internal Q&A without sending data to OpenAI.  

⭐ Features
🔹 1. Local RAG (Retrieval-Augmented Generation)  
Loads internal documents (PDF/CSV/TXT), encodes them, stores them in FAISS, and retrieves answers instantly.

🔹 2. Slack Integration  
Ask questions by mentioning the bot:
```
@Knowledge Assistant What is our leave policy?
```
Bot responds with precise, filtered answer snippets.

🔹 3. Keyword-Level Filtering  
Improves accuracy by returning only lines relevant to user query (instead of entire paragraphs).

🔹 4. Contact Lookup  
Every answer automatically includes the correct contact person:
```
For further assistance:
Name: Priya Iyer  
Department: Finance  
Role: Senior Accountant  
Email: priya.iyer@tcsdemo.com
```

🔹 5. Private & Offline  
No external APIs  
No OpenAI  
No cloud calls  
Your documents stay local.  

🔹 6. Sandbox-First Architecture  
Before deploying to Slack, you test everything locally (FastAPI Dashboard + Evaluator + Logs).

📁 Project Structure
```
ai_knowledge_assistant/
│
├── app.py                     # Slack Bot (Flask + Slack Bolt)
├── knowledge_base.py          # Build FAISS index from /data
├── train_faiss_hard.py        # Hard-embed curated Q&A
│
├── data/                      # PDFs, CSVs, TXT files
│   ├── tcs_policies.pdf
│   ├── client_faqs.txt
│   ├── employee_directory.csv
|   ├── project_workflows.csv
│   └── automation_guidelines.pdf
│
├── reference_answers.csv      # Curated answers for hard embedding
├── contacts.csv               # Contact directory
│
├── knowledge_index/           # FAISS index (index.faiss + index.pkl)
│
|__ .env                       # Slack secrets (ignored in Git)
```


⚙️ Setup Instructions  
1️⃣ Install dependencies
```
pip install -r requirements.txt
```
Or manually:
```
pip install slack-bolt flask python-dotenv \
            sentence-transformers faiss-cpu \
            langchain-community langchain-text-splitters pandas
```

2️⃣ Add your Slack credentials  
Create .env:
```
SLACK_BOT_TOKEN=xoxb-************
SLACK_SIGNING_SECRET=************
```
Never commit .env.

3️⃣ Build the Knowledge Base (FAISS index)  
```
python knowledge_base.py
```
OR (for curated Q&A):
```
python train_faiss_hard.py
```
This creates:
```
knowledge_index/
    ├── index.faiss
    └── index.pkl
```

4️⃣ Run the Slack Bot  
```
python app.py
```
Bot runs on:
```
http://127.0.0.1:3000
```

5️⃣ Start ngrok for Slack events
```
ngrok http 3000
```
Copy the HTTPS URL and paste into Slack:
```
Event Subscriptions → Request URL:
https://<ngrok-url>/slack/events
```
Enable event:
```
Subscribe to Bot Events: app_mention
```
Save.

6️⃣ Add bot to Slack channel
Then test:
```
@Knowledge Assistant Who approves work-from-home?
```

🔥 How the RAG Engine Works
1. Documents → Text Chunks
PDFs / CSVs / TXT → cleaned → split into 300–500 token chunks.
2. Embedding
Using all-MiniLM-L6-v2
(very fast, great for knowledge retrieval)
3. FAISS Storage
Vectors saved into FAISS for instant similarity search.
4. Query Flow
User question → embedding → FAISS search (k=3) → keyword filter → formatted answer.
5. Contact Logic
Matches department (HR/IT/Admin/Finance/etc.)
Appends contact block from contacts.csv.

📊 Evaluation Workflow (Optional but Powerful)  
For scoring bot accuracy:  
✔ batch_test.py  
Posts all questions to Slack automatically.  
✔ evaluate_local.py  
Compares bot answers vs reference answers using semantic similarity.  

Outputs:  
evaluation_report.csv  
accuracy score  
relevance score  
Great for iterative tuning.  

🔐 Security & Enterprise Notes  
✔ No OpenAI or cloud API  
✔ Works offline  
✔ Secrets stored in .env  
✔ All documents stay local  
✔ Ideal for internal policy assistants  

🚀 Future Enhancements (Roadmap)  
Add GPT/LLaMA rewriter for more human answers  
Multi-turn memory (“and what about sick leave?”)  
Admin dashboard for logs, performance, and accuracy  
Real-time ingestion from GDrive, SharePoint, Confluence  
Deploy on AWS EC2 / Docker  

👨‍💻 Author
Dishant Makawana
AI Automation & Workflow Developer
📍 Ahmedabad, Gujarat, India

💡 Building real-world automations that merge data, AI, and human context into practical business systems.

📜 License
Open for learning and demonstration purposes.
Use, modify, or expand freely with proper credit.
