import pymupdf
import numpy as np
import faiss
import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)


def save_faiss(index, chunks, path="vector_score"):
    os.makedirs(path, exist_ok=True)

    faiss.write_index(index, f"{path}/index.faiss")

    with open(f"{path}/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def load_faiss(path="vector_score"):
    index = faiss.read_index(f"{path}/index.faiss")

    with open(f"{path}/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, chunks


def file_embedding(file_list: list):
    chunks = []
    embeddings = []
    for file_name in file_list:
        doc = pymupdf.open(file_name) 
        
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            p_chunk = splitter.split_text(text)

            for chunk_id, chunk in enumerate(p_chunk):
                chunks.append({
                    "text": chunk,
                    "metadata": {
                        "file": file_name,
                        "page": i,
                        "c_id": chunk_id+1
                    }}
                )
                embeddings.append(model.encode(chunk))
        

    embeddings = np.array(embeddings, dtype=np.float32)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    save_faiss(index, chunks, path = "vector_score")
    
    return index, chunks

def get_pdf_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.lower().endswith(".pdf"):
            files.append(os.path.join(folder, file))
    return files

file_list = get_pdf_files("pdfs")
file_embedding(file_list)  