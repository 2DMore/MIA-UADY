"""Throwaway script: run once to pick MIN_SCORE. Requires GOOGLE_API_KEY in .env."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from app.chunk import chunk_text
from app.clean import drop_lines, find_boilerplate
from app.embed import Embedder
from app.loaders import load_document
from app.store import VectorStore

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_calibration"

QUESTIONS = [
    "Quien era Prometeo y por que fue castigado?",  # dominio
    "Que le ocurrio a Edipo cuando descubrio la verdad sobre su origen?",  # dominio
    "Que le paso a Narciso segun las Metamorfosis?",  # dominio
    "Quien es Odin y que papel tiene en Ragnarok?",  # imposible: mitologia nordica
    "Cual es la capital de Francia?",  # imposible: control sin relacion
]


def main():
    embedder = Embedder()
    store = VectorStore(str(CHROMA_DIR))
    docs = [load_document(p) for p in sorted(DATA_DIR.glob("*.txt"))]
    boilerplate = find_boilerplate([d["text"] for d in docs])
    for doc in docs:
        chunks = chunk_text(drop_lines(doc["text"], boilerplate), source=doc["source"])
        if not chunks:
            continue
        vectors = embedder.embed([c["text"] for c in chunks])
        ids = [f"{doc['source']}-{c['chunk_index']}" for c in chunks]
        metadatas = [{"source": doc["source"], "chunk_index": c["chunk_index"]} for c in chunks]
        store.add(ids=ids, texts=[c["text"] for c in chunks], embeddings=vectors, metadatas=metadatas)
        print(f"indexed {doc['source']}: {len(chunks)} chunks")

    print("\nScores:")
    for question in QUESTIONS:
        vector = embedder.embed([question])[0]
        matches = store.query(vector, top_k=3)
        best = matches[0]["score"] if matches else None
        print(f"- {question!r} -> best_score={best}")


if __name__ == "__main__":
    main()
