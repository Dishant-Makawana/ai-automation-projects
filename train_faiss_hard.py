import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Try both possible imports depending on LangChain version
try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

# === PATH CONFIG ===
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "reference_answers.csv")
INDEX_DIR = os.path.join(BASE_DIR, "knowledge_index")

# === LOAD DATA ===
df = pd.read_csv(CSV_PATH)

if "prompt" not in df.columns or "reference_answer" not in df.columns:
    raise ValueError("❌ CSV must have 'prompt' and 'reference_answer' columns.")

# === PREPARE DOCUMENTS ===
docs = []
for i, row in df.iterrows():
    q = str(row["prompt"]).strip()
    a = str(row["reference_answer"]).strip()
    content = f"Question: {q}\nAnswer: {a}"
    docs.append(Document(page_content=content))

print(f"✅ Loaded {len(docs)} Q&A pairs for hard FAISS training.")

# === CLEAN OLD INDEX ===
if os.path.exists(INDEX_DIR):
    for f in os.listdir(INDEX_DIR):
        os.remove(os.path.join(INDEX_DIR, f))
    print("🧹 Old FAISS index cleaned.")

# === EMBEDDINGS & VECTORSTORE ===
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Recreate FAISS index from scratch
db = FAISS.from_documents(docs, embeddings)
db.save_local(INDEX_DIR)

print(f"🎯 Hard retraining complete! FAISS index saved to:\n{INDEX_DIR}")
