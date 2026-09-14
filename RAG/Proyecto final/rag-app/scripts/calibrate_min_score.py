"""Throwaway script: run once to pick MIN_SCORE. Requires GOOGLE_API_KEY in .env."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from app.chunk import chunk_text
from app.embed import Embedder
from app.loaders import load_document
from app.store import VectorStore

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_calibration"

QUESTIONS = [
    "Que es la busqueda en anchura (BFS)?",
    "Que es una funcion de activacion en una red neuronal?",
    "Que es una capa convolucional?",
    "Que dice el material sobre los Transformers y los LLMs?",  # impossible question
]


def main():
    embedder = Embedder()
    store = VectorStore(str(CHROMA_DIR))
    for pdf_path in sorted(DATA_DIR.glob("*.pdf")):
        doc = load_document(pdf_path)
        chunks = chunk_text(doc["text"], source=doc["source"])
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
