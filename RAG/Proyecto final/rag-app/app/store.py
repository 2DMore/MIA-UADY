import chromadb

COLLECTION_NAME = "rag_chunks"


class VectorStore:
    def __init__(self, persist_directory: str):
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        self._collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def query(self, embedding: list[float], top_k: int = 3) -> list[dict]:
        result = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        matches = []
        for doc_id, text, metadata, distance in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            matches.append({
                "id": doc_id,
                "text": text,
                "source": metadata.get("source"),
                "score": 1 - distance,
            })
        return matches

    def count(self) -> int:
        return self._collection.count()

    def list_sources(self) -> list[dict]:
        result = self._collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for metadata in result["metadatas"]:
            source = metadata.get("source", "desconocido")
            counts[source] = counts.get(source, 0) + 1
        return [{"source": source, "chunks": chunks} for source, chunks in counts.items()]
