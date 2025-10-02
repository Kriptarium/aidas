
# AIDAS-HT Chatbot (MVP)

FastAPI + TF-IDF tabanlı RAG ile hasar tespit eğitimi sohbet botu.
- `/` ana sayfada arayüz
- `/ask`, `/quiz/start`, `/quiz/submit`, `/health` API'leri

## Lokal Çalıştırma
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://127.0.0.1:8000/
```

## Render Yayınlama (Docker yok)
- Environment: Python
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
