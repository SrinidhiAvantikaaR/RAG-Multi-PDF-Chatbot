import pymupdf
import numpy as np
import faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)

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
   
    return index, chunks

file_list = ['.pdf', 'sample_test_document.pdf']
file_embedding(file_list)  