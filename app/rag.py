
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

@dataclass
class DocChunk:
    doc_id: str
    title: str
    chunk_id: int
    text: str
    source_path: str

class SimpleRAG:
    def __init__(self, kb_dir: str = 'kb'):
        self.kb_dir = Path(kb_dir)
        self.chunks: List[DocChunk] = []
        self.vectorizer = None
        self.matrix = None
        self._build_index()

    def _read_pdf(self, path: Path) -> str:
        try:
            r = PdfReader(str(path))
            texts = []
            for page in r.pages:
                t = page.extract_text() or ""
                texts.append(t)
            return "\n".join(texts)
        except Exception:
            return ""

    def _clean(self, t: str) -> str:
        t = re.sub(r"\s+", " ", t)
        return t.strip()

    def _split(self, text: str) -> List[str]:
        chunks = []
        i = 0
        while i < len(text):
            chunk = text[i:i+CHUNK_SIZE]
            chunks.append(chunk)
            i += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def _build_index(self):
        pdfs = sorted(self.kb_dir.glob("*.pdf"))
        for p in pdfs:
            raw = self._read_pdf(p)
            if not raw:
                continue
            raw = self._clean(raw)
            parts = self._split(raw)
            title = p.stem
            for ci, part in enumerate(parts):
                self.chunks.append(DocChunk(
                    doc_id=p.name, title=title, chunk_id=ci, text=part, source_path=str(p.name)
                ))
        corpus = [c.text for c in self.chunks]
        if corpus:
            self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", max_df=0.9)
            self.matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, k: int = 5):
        if not self.chunks or self.matrix is None:
            return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        top_idx = sims.argsort()[::-1][:k]
        return [(self.chunks[i], float(sims[i])) for i in top_idx if sims[i] > 0.0]

    def answer(self, query: str, k: int = 5) -> Dict:
        ctx = self.retrieve(query, k=k)
        if not ctx:
            return {"answer":"KB’de ilgili içerik bulunamadı.", "contexts":[], "disclaimer":_DISCLAIMER}
        joined = " ".join([c.text for c,_ in ctx])[:1200]
        cites = [{"title": c.title, "doc": c.doc_id, "chunk_id": c.chunk_id} for c,_ in ctx]
        ans = "Eğitimsel özet (KB tabanlı):\n" + joined
        return {"answer": ans, "contexts": cites, "disclaimer": _DISCLAIMER}

_DISCLAIMER = "Bu çıktı eğitim amaçlıdır; resmi hasar kararı için yetkili kurumların prosedürleri esastır."
