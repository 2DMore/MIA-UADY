import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.clean import find_boilerplate, drop_lines
from app.loaders import load_document
from app.chunk import chunk_text
from app.embed import Embedder
from app.store import VectorStore
from app.generate import Generator, ABSTENTION_MESSAGE

load_dotenv()

CHROMA_PATH = os.environ.get("CHROMA_PATH", "chroma")
DATA_PATH = os.environ.get("DATA_PATH", "data")
MIN_SCORE = float(os.environ.get("MIN_SCORE", "0.5"))
DEFAULT_TOP_K = 3

app = FastAPI(title="RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VectorStore(CHROMA_PATH)
embedder = Embedder()
generator = Generator()


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


class Citation(BaseModel):
    id: str
    source: str
    text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool


@app.get("/health")
def health():
    try:
        count = store.count()
        sources = store.list_sources()
        chroma_ok = True
    except Exception:
        count = 0
        sources = []
        chroma_ok = False
    return {"status": "ok", "chroma_ok": chroma_ok, "indexed_chunks": count, "sources": sources}


def corpus_boilerplate() -> frozenset[str]:
    """Lineas repetidas entre los documentos de texto de DATA_PATH (menus, anuncios)."""
    texts = []
    for path in Path(DATA_PATH).glob("*"):
        if path.suffix.lower() in (".txt", ".md"):
            try:
                texts.append(load_document(path)["text"])
            except Exception:
                continue
    return find_boilerplate(texts)


@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    documents_indexed = 0
    chunks_indexed = 0
    errors = []
    saved = []
    for upload in files:
        try:
            dest = Path(DATA_PATH) / upload.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(await upload.read())
            saved.append((upload.filename, dest))
        except Exception as exc:
            errors.append({"file": upload.filename, "error": str(exc)})
    boilerplate = corpus_boilerplate()
    for filename, dest in saved:
        try:
            doc = load_document(dest)
            text = drop_lines(doc["text"], boilerplate)
            chunks = chunk_text(text, source=doc["source"])
            if not chunks:
                continue
            vectors = embedder.embed([c["text"] for c in chunks])
            ids = [f"{doc['source']}-{c['chunk_index']}-{uuid.uuid4().hex[:8]}" for c in chunks]
            metadatas = [{"source": doc["source"], "chunk_index": c["chunk_index"]} for c in chunks]
            store.add(ids=ids, texts=[c["text"] for c in chunks], embeddings=vectors, metadatas=metadatas)
            documents_indexed += 1
            chunks_indexed += len(chunks)
        except Exception as exc:
            errors.append({"file": filename, "error": str(exc)})
    return {"documents_indexed": documents_indexed, "chunks_indexed": chunks_indexed, "errors": errors}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    question = request.question.strip()
    if not question:
        return QueryResponse(answer=ABSTENTION_MESSAGE, citations=[], abstained=True)
    top_k = request.top_k or DEFAULT_TOP_K
    try:
        vector = embedder.embed([question])[0]
        matches = store.query(vector, top_k=top_k)
    except Exception:
        return QueryResponse(answer=ABSTENTION_MESSAGE, citations=[], abstained=True)
    best_score = matches[0]["score"] if matches else 0.0
    if not matches or best_score < MIN_SCORE:
        return QueryResponse(answer=ABSTENTION_MESSAGE, citations=[], abstained=True)
    try:
        answer = generator.generate(question, matches)
    except Exception:
        return QueryResponse(answer=ABSTENTION_MESSAGE, citations=[], abstained=True)
    citations = [Citation(**m) for m in matches]
    return QueryResponse(answer=answer, citations=citations, abstained=False)
