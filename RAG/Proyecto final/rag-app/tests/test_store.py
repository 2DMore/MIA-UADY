from app.store import VectorStore


def test_add_and_query_returns_nearest_neighbor(tmp_path):
    store = VectorStore(str(tmp_path))
    store.add(
        ids=["c1", "c2"],
        texts=["gatos y perros", "finanzas y bancos"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        metadatas=[{"source": "animales.md"}, {"source": "dinero.md"}],
    )
    results = store.query(embedding=[0.9, 0.1], top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "c1"
    assert results[0]["source"] == "animales.md"
    assert results[0]["score"] > 0.9


def test_persistence_across_instances(tmp_path):
    store1 = VectorStore(str(tmp_path))
    store1.add(ids=["c1"], texts=["contenido"], embeddings=[[1.0, 0.0]], metadatas=[{"source": "a.md"}])
    store2 = VectorStore(str(tmp_path))
    assert store2.count() == 1


def test_query_top_k_limits_results(tmp_path):
    store = VectorStore(str(tmp_path))
    store.add(
        ids=["c1", "c2", "c3"],
        texts=["a", "b", "c"],
        embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
        metadatas=[{"source": "a.md"}, {"source": "b.md"}, {"source": "c.md"}],
    )
    results = store.query(embedding=[1.0, 0.0], top_k=2)
    assert len(results) == 2


def test_list_sources_returns_empty_list_when_no_documents(tmp_path):
    store = VectorStore(str(tmp_path))
    assert store.list_sources() == []


def test_list_sources_groups_chunk_counts_by_source(tmp_path):
    store = VectorStore(str(tmp_path))
    store.add(
        ids=["c1", "c2", "c3"],
        texts=["a", "b", "c"],
        embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
        metadatas=[
            {"source": "a.pdf", "chunk_index": 0},
            {"source": "a.pdf", "chunk_index": 1},
            {"source": "b.pdf", "chunk_index": 0},
        ],
    )
    sources = store.list_sources()
    assert sorted(sources, key=lambda s: s["source"]) == [
        {"source": "a.pdf", "chunks": 2},
        {"source": "b.pdf", "chunks": 1},
    ]
