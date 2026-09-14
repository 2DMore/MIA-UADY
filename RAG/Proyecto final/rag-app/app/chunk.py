def chunk_text(text: str, source: str, chunk_size: int = 300, overlap: int = 60) -> list[dict]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks = []
    start = 0
    index = 0
    while start < len(words):
        chunk_words = words[start:start + chunk_size]
        chunks.append({
            "text": " ".join(chunk_words),
            "source": source,
            "chunk_index": index,
        })
        if start + chunk_size >= len(words):
            break
        start += step
        index += 1
    return chunks
