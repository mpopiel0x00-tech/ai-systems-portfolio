from fastapi import FastAPI
from pydantic import BaseModel

from src.query_rag import ask_query

app = FastAPI(title="RAG Eval API")

class AskRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    answer = ask_query(req.query)
    return {
        "query": req.query,
        "answer": answer,
    }

