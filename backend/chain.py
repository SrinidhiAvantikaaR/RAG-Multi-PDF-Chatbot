from ingest import load_faiss
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

llm=genai.GenerativeModel("gemini-2.5-flash")

model=SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_chunks(question, index, chunks, k=3):
    query_embedding=model.encode(question)

    query_embedding=np.array(
        [query_embedding],
        dtype=np.float32
    )

    faiss.normalize_L2(query_embedding)
    scores,indices=index.search(query_embedding,k)

    retrieved_chunks = []

    for score, idx in zip(scores[0],indices[0]):
        if idx==-1:
            continue
        retrieved_chunks.append({
            "text":chunks[idx]["text"],
            "metadata":chunks[idx]["metadata"],
            "score":float(score)
        })
    return retrieved_chunks

def get_answer(query, chat_history=None):
    index, chunks=load_faiss()
    retrieved_chunks = retrieve_chunks(query, index, chunks)
    context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)
    history = ""

    for item in chat_history[-3:]:
        history += (
            f"User: {item['user']}\n"
            f"Assistant: {item['assistant']}\n"
        )
    
    prompt = f"""
You are a helpful PDF question-answering assistant.

Answer ONLY using the provided context.

If the answer is not found in the given context, give a reply like,
"I don't find any answer in the given documents."

Chat Conversation History:
{history}

Context:
{context}

Question:
{query}

Answer:
"""
    
    response = llm.generate_content(prompt)

    sources = []
    for chunk in retrieved_chunks:
        metadata = chunk["metadata"]
        sources.append({
            "file": metadata["file"],
            "page": metadata["page"],
            "chunk": metadata["c_id"]
        })
    
    return {"answer": response.text,
            "sources": sources}
