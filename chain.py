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

index, chunks=load_faiss()
model=SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_chunks(question,k=3):
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

