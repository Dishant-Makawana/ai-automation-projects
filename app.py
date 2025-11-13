from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import re
import pandas as pd

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

# Load environment variables
load_dotenv()

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# Initialize Flask
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# ============================================
#      LOAD KNOWLEDGE BASE + CONTACT FILE
# ============================================

print("🔍 Loading Knowledge Base...")
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

KNOWLEDGE_PATH = r"C:\Users\Bandhkam\OneDrive\Desktop\AI_AUTOMATION_SPECIALIST\projects\ai_knowledge_assistant\knowledge_index"
CONTACTS_PATH = r"C:\Users\Bandhkam\OneDrive\Desktop\AI_AUTOMATION_SPECIALIST\projects\ai_knowledge_assistant\contacts.csv"

db = FAISS.load_local(KNOWLEDGE_PATH, embeddings, allow_dangerous_deserialization=True)
print("✅ Knowledge Base Ready.")

contacts_df = pd.read_csv(CONTACTS_PATH)


# ============================================
#            CLEANING DOC → ANSWER
# ============================================

def extract_clean_answer(raw_text: str):
    """
    Clean FAISS doc that contains:
        Question:
        Answer:
        (sometimes multiple Q/A blocks)
    Returns only the first usable Answer block.
    Extracts an email (if any) separately.
    """

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    found_email = email_match.group(0) if email_match else None

    # Split into lines
    lines = raw_text.replace("\r", "").split("\n")

    # Remove lines starting with "Question:"
    filtered = [ln for ln in lines if not ln.strip().lower().startswith("question:")]

    combined = "\n".join(filtered)

    # Extract the first Answer:
    ans_match = re.search(
        r"Answer\s*:\s*(.*?)(?=\n\s*Question\s*:|\Z)",
        combined,
        flags=re.IGNORECASE | re.DOTALL
    )

    if ans_match:
        answer = ans_match.group(1).strip()
    else:
        answer = combined.strip()

    # Remove emails & parentheses from visible paragraph
    answer = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', answer)
    answer = re.sub(r'\([^)]*\)', '', answer)
    answer = re.sub(r'\s{2,}', ' ', answer).strip()

    return answer, found_email


# ============================================
#     FETCH CONTACT DETAILS FROM CSV
# ============================================

def get_contact_card(email):
    if email is None:
        return None

    row = contacts_df[contacts_df["Email"].str.lower() == email.lower()]

    if row.empty:
        return None

    r = row.iloc[0]

    return (
        "🧑‍💼 *Contact Person*\n"
        f"• *Name:* {r['Name']}\n"
        f"• *Department:* {r['Department']}\n"
        f"• *Role:* {r['Role']}\n"
        f"• *Email:* {r['Email']}"
    )


# ============================================
#       SEARCH + FORMAT FINAL ANSWER
# ============================================

def get_answer_from_knowledge_base(query):
    docs = db.similarity_search(query, k=1)
    if not docs:
        return "I couldn't find anything on that topic.", None

    raw = docs[0].page_content

    clean_ans, found_email = extract_clean_answer(raw)

    return clean_ans, found_email


# ============================================
#               SLACK HANDLER
# ============================================

@app.event("app_mention")
def handle_app_mentions(body, say):
    user = body["event"]["user"]
    text = body["event"]["text"]

    clean_query = text.split(">", 1)[-1].strip()

    if clean_query.lower() in ["hi", "hello", "hey"]:
        say(f"Hey <@{user}> 👋 I’m live and ready! Ask me anything about policies, HR, IT, admin, or workflows.")
        return

    say(f"🔎 Searching for answers on: *{clean_query}* ...")

    answer, email = get_answer_from_knowledge_base(clean_query)

    final_msg = f"📘 *Here's the most accurate answer I found:*\n\n{answer}"

    say(final_msg)

    # If a contact person exists, append it
    card = get_contact_card(email)
    if card:
        say(card)


# ============================================
#              SLACK ROUTE
# ============================================

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json()
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    return handler.handle(request)


# ============================================
#              RUN FLASK
# ============================================

if __name__ == "__main__":
    flask_app.run(port=3000)
