from __future__ import annotations
import os, json, datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
from .rag import SimpleRAG

APP_NAME = "AIDAS-HT Chatbot (MVP)"
KB_DIR = "kb"

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = SimpleRAG(KB_DIR)

class AskBody(BaseModel):
    user_id: str = "demo"
    question: str
    k: int = 5

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "kb_docs": len(list(Path(KB_DIR).glob("*.pdf")))}

@app.post("/ask")
def ask(body: AskBody):
    res = rag.answer(body.question, k=body.k)
    return res

# --- Minimal quiz endpoints ---
QUIZ_FILE = Path(__file__).parent / "quizzes.json"
if not QUIZ_FILE.exists():
    QUIZ_FILE.write_text(json.dumps([
        {"id":"Q1", "module":"Temel", "text":"Çapraz çatlaklar çoğunlukla hangi etkiyle ilişkilidir?",
         "choices":["Isıl genleşme","Kesme etkisi","Temel oturması","Boyutsal büzülme"], "correct":1},
        {"id":"Q2", "module":"Form", "text":"HT formunda taşıyıcı sistem alanı aşağıdakilerden hangisi değildir?",
         "choices":["Betonarme", "Çelik", "Yığma", "PVC doğrama"], "correct":3}
    ], ensure_ascii=False, indent=2), encoding="utf-8")

with QUIZ_FILE.open(encoding="utf-8") as f:
    QUIZ_BANK = json.load(f)

@app.get("/quiz/start")
def quiz_start(limit: int = 5):
    return {"items": QUIZ_BANK[:limit]}

class QuizAnswer(BaseModel):
    id: str
    answer: int

class QuizSubmitBody(BaseModel):
    user_id: str = "demo"
    answers: List[QuizAnswer]

@app.post("/quiz/submit")
def quiz_submit(body: QuizSubmitBody):
    key = {q["id"]: q["correct"] for q in QUIZ_BANK}
    score = 0
    details = []
    for a in body.answers:
        correct = key.get(a.id, -999)
        ok = (a.answer == correct)
        score += int(ok)
        details.append({"id": a.id, "ok": ok, "your": a.answer, "correct": correct})
    return {"score": score, "total": len(body.answers), "details": details}

# Simple static landing (useful when deployed)
@app.get("/")
def root():
    return {
        "message": "AIDAS-HT Chatbot çalışıyor. /frontend/index.html dosyasını statik servis ile yayınlayın veya bu API'yi bir web istemcisiyle kullanın.",
        "endpoints": ["/ask", "/quiz/start", "/quiz/submit", "/health"]
    }
