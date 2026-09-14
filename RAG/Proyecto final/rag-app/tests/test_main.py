from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)


def test_health_returns_ok_chunk_count_and_sources(monkeypatch):
    class FakeStore:
        def count(self):
            return 5

        def list_sources(self):
            return [{"source": "a.pdf", "chunks": 5}]

    monkeypatch.setattr(main, "store", FakeStore())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["chroma_ok"] is True
    assert body["indexed_chunks"] == 5
    assert body["sources"] == [{"source": "a.pdf", "chunks": 5}]


def test_health_never_returns_500_when_store_fails(monkeypatch):
    class FailingStore:
        def count(self):
            raise RuntimeError("chroma unavailable")

        def list_sources(self):
            raise RuntimeError("chroma unavailable")

    monkeypatch.setattr(main, "store", FailingStore())
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["chroma_ok"] is False
    assert body["sources"] == []


def test_query_abstains_on_blank_question():
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True
    assert body["citations"] == []


def test_query_abstains_when_best_score_below_threshold(monkeypatch):
    class FakeEmbedder:
        def embed(self, texts):
            return [[0.0, 0.0]]

    class FakeStore:
        def query(self, embedding, top_k):
            return [{"id": "c1", "source": "a.pdf", "text": "algo", "score": 0.1}]

    monkeypatch.setattr(main, "embedder", FakeEmbedder())
    monkeypatch.setattr(main, "store", FakeStore())
    monkeypatch.setattr(main, "MIN_SCORE", 0.5)
    response = client.post("/query", json={"question": "Que son los transformers?"})
    body = response.json()
    assert body["abstained"] is True
    assert body["answer"] == main.ABSTENTION_MESSAGE


def test_query_returns_answer_with_citations_when_evidence_found(monkeypatch):
    class FakeEmbedder:
        def embed(self, texts):
            return [[1.0, 0.0]]

    class FakeStore:
        def query(self, embedding, top_k):
            return [{"id": "c1", "source": "chapter03.pdf", "text": "BFS explora por niveles", "score": 0.9}]

    class FakeGenerator:
        def generate(self, question, chunks):
            return "BFS explora por niveles [1]."

    monkeypatch.setattr(main, "embedder", FakeEmbedder())
    monkeypatch.setattr(main, "store", FakeStore())
    monkeypatch.setattr(main, "generator", FakeGenerator())
    monkeypatch.setattr(main, "MIN_SCORE", 0.5)
    response = client.post("/query", json={"question": "Que es BFS?"})
    body = response.json()
    assert body["abstained"] is False
    assert body["answer"] == "BFS explora por niveles [1]."
    assert body["citations"][0]["source"] == "chapter03.pdf"


def test_query_never_returns_500_on_internal_error(monkeypatch):
    class FailingEmbedder:
        def embed(self, texts):
            raise RuntimeError("quota exceeded")

    monkeypatch.setattr(main, "embedder", FailingEmbedder())
    response = client.post("/query", json={"question": "Que es BFS?"})
    assert response.status_code == 200
    assert response.json()["abstained"] is True


def test_query_never_returns_500_when_generation_fails(monkeypatch):
    class FakeEmbedder:
        def embed(self, texts):
            return [[1.0, 0.0]]

    class FakeStore:
        def query(self, embedding, top_k):
            return [{"id": "c1", "source": "chapter03.pdf", "text": "BFS explora por niveles", "score": 0.9}]

    class FailingGenerator:
        def generate(self, question, chunks):
            raise RuntimeError("model not found")

    monkeypatch.setattr(main, "embedder", FakeEmbedder())
    monkeypatch.setattr(main, "store", FakeStore())
    monkeypatch.setattr(main, "generator", FailingGenerator())
    monkeypatch.setattr(main, "MIN_SCORE", 0.5)
    response = client.post("/query", json={"question": "Que es BFS?"})
    assert response.status_code == 200
    body = response.json()
    assert body["abstained"] is True
    assert body["answer"] == main.ABSTENTION_MESSAGE


def test_ingest_indexes_uploaded_text_file(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_PATH", str(tmp_path))

    class FakeEmbedder:
        def embed(self, texts):
            return [[1.0, 0.0] for _ in texts]

    class FakeStore:
        def __init__(self):
            self.added = []

        def add(self, ids, texts, embeddings, metadatas):
            self.added.append((ids, texts, embeddings, metadatas))

    fake_store = FakeStore()
    monkeypatch.setattr(main, "embedder", FakeEmbedder())
    monkeypatch.setattr(main, "store", fake_store)
    file_content = ("palabra " * 50).encode("utf-8")
    response = client.post("/ingest", files={"files": ("nota.md", file_content, "text/markdown")})
    body = response.json()
    assert body["documents_indexed"] == 1
    assert body["chunks_indexed"] >= 1
    assert len(fake_store.added) == 1
