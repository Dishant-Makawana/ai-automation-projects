import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader

def build_knowledge_base(data_folder="data"):
    docs = []
    for file in os.listdir(data_folder):
        path = os.path.join(data_folder, file)
        print(f"📄 Reading: {file}")
        try:
            if file.endswith(".txt"):
                docs.extend(TextLoader(path).load())
            elif file.endswith(".csv"):
                docs.extend(CSVLoader(path).load())
            elif file.endswith(".pdf"):
                docs.extend(PyPDFLoader(path).load())
        except Exception as e:
            print(f"⚠️ Error loading {file}: {e}")

    if not docs:
        print("❌ No documents found. Please check your data folder path.")
        return

    print(f"✅ Loaded {len(docs)} documents. Now embedding...")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local("knowledge_index")

    print("🎯 Knowledge base created and saved as 'knowledge_index'")

if __name__ == "__main__":
    build_knowledge_base()
