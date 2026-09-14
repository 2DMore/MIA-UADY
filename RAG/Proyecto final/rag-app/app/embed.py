import os

from google import genai

EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_BATCH_SIZE = 20


class EmbeddingError(RuntimeError):
    pass


def _default_client():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EmbeddingError("GOOGLE_API_KEY is not set")
    return genai.Client(api_key=api_key)


class Embedder:
    def __init__(self, client=None, model: str = EMBEDDING_MODEL, batch_size: int = DEFAULT_BATCH_SIZE):
        self._client = client
        self._model = model
        self._batch_size = batch_size

    @property
    def client(self):
        if self._client is None:
            self._client = _default_client()
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start:start + self._batch_size]
            response = self.client.models.embed_content(model=self._model, contents=batch)
            vectors.extend(embedding.values for embedding in response.embeddings)
        return vectors
