from langchain_community.vectorstores import FAISS

def create_vector_store(docs, embeddings):
    db = FAISS.from_documents(docs, embeddings)
    return db

def get_relevant_docs(db, query):
    return db.similarity_search(query, k=3)   # 🔥 reduce from default (usually 4–10)