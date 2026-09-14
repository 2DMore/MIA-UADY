import pytest
from app.embed import Embedder, EmbeddingError


class FakeEmbedding:
    def __init__(self, values):
        self.values = values


class FakeEmbedResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


class FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents):
        self.calls.append((model, contents))
        return FakeEmbedResponse([FakeEmbedding([float(len(t))]) for t in contents])


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_embed_returns_empty_list_for_empty_input():
    embedder = Embedder(client=FakeClient())
    assert embedder.embed([]) == []


def test_embed_returns_one_vector_per_text():
    embedder = Embedder(client=FakeClient(), batch_size=10)
    result = embedder.embed(["hola", "mundo!!"])
    assert result == [[4.0], [7.0]]


def test_embed_batches_requests_by_batch_size():
    fake_client = FakeClient()
    embedder = Embedder(client=fake_client, batch_size=2)
    embedder.embed(["a", "b", "c", "d", "e"])
    assert len(fake_client.models.calls) == 3
    assert [len(contents) for _, contents in fake_client.models.calls] == [2, 2, 1]


def test_embed_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    embedder = Embedder()
    with pytest.raises(EmbeddingError):
        embedder.embed(["hola"])
