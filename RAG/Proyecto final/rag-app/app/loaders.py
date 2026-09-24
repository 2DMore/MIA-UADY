from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument

from app.clean import clean_text


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_docx(path: Path) -> str:
    doc = DocxDocument(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def load_text(path: Path) -> str:
    # Solo texto plano/markdown: suele venir de paginas web con menus y anuncios.
    return clean_text(path.read_text(encoding="utf-8"))


LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".md": load_text,
    ".txt": load_text,
}


def load_document(path: Path) -> dict:
    ext = path.suffix.lower()
    if ext not in LOADERS:
        raise ValueError(f"Unsupported file extension: {ext}")
    text = LOADERS[ext](path)
    return {"text": text, "source": path.name, "title": path.stem}
