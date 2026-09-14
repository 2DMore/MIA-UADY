import pytest
from app.chunk import chunk_text


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("", source="empty.md") == []


def test_chunk_text_splits_with_overlap_using_custom_sizes():
    text = " ".join(f"w{i}" for i in range(7))  # w0..w6
    chunks = chunk_text(text, source="doc.md", chunk_size=3, overlap=1)
    assert [c["text"] for c in chunks] == ["w0 w1 w2", "w2 w3 w4", "w4 w5 w6"]
    assert [c["chunk_index"] for c in chunks] == [0, 1, 2]
    assert all(c["source"] == "doc.md" for c in chunks)


def test_chunk_text_default_parameters_produce_expected_chunk_count():
    text = " ".join(f"tok{i}" for i in range(900))
    chunks = chunk_text(text, source="doc.md")
    assert len(chunks) == 4
    assert chunks[0]["text"].split()[0] == "tok0"
    assert chunks[1]["text"].split()[0] == "tok240"
    assert chunks[3]["text"].split()[-1] == "tok899"


def test_chunk_text_raises_when_overlap_not_smaller_than_chunk_size():
    with pytest.raises(ValueError, match="overlap must be smaller than chunk_size"):
        chunk_text("a b c", source="doc.md", chunk_size=3, overlap=3)
