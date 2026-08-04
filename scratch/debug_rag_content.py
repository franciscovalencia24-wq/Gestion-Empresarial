import os
import sys
sys.path.append(os.getcwd())
from src.intelligence.rag_advisor import RAGAdvisor

def debug_rag():
    advisor = RAGAdvisor()
    q = "¿Qué requisitos debe cumplir un intermediario de valores para operar en Chile?"
    print(f"Question: {q}")
    
    if not advisor.vector_store:
        print("Vector store not loaded. Loading now...")
        from langchain_community.vectorstores import Chroma
        advisor.vector_store = Chroma(persist_directory=advisor.persist_dir, embedding_function=advisor.embeddings)

    docs = advisor.vector_store.similarity_search(q, k=8)
    print(f"Found {len(docs)} documents.")
    
    for i, d in enumerate(docs):
        print(f"\n--- DOCUMENT {i+1} ---")
        print(f"Source: {d.metadata.get('source')}")
        print(f"Content (first 400 chars): {d.page_content[:400]}")

if __name__ == "__main__":
    debug_rag()
