from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os

from ingest import file_embedding
from chain import get_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # For development
    allow_credentials=False,      # Don't use True with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "Multi PDF RAG Chatbot Backend Running"}


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):

    if len(files) == 0:
        return {"message": "No files uploaded."}

    paths = []

    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print("UPLOAD_FOLDER:", UPLOAD_FOLDER)
        print("Exists:", os.path.exists(UPLOAD_FOLDER))

        paths.append(filepath)

    if len(paths) == 0:
        return {"message": "No valid PDF files found."}

    try:
        file_embedding(paths)

        return {
            "message": f"{len(paths)} PDF(s) indexed successfully!"
        }

    except Exception as e:
        return {
            "message": f"Error while indexing PDFs: {str(e)}"
        }


class ChatRequest(BaseModel):
    question: str
    history: list = []


@app.post("/chat")
def chat(req: ChatRequest):

    try:

        result = get_answer(
            req.question,
            req.history
        )

        # get_answer already returns:
        # {
        #     "answer": "...",
        #     "sources": [...]
        # }

        return result

    except FileNotFoundError:
        return {
            "answer": "Please upload and index PDF files first.",
            "sources": []
        }

    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": []
        }