from pathlib import Path
import pytest
from app import loaders


def test_load_text_reads_utf8_content(tmp_path):
    file_path = tmp_path / "note.md"
    file_path.write_text("# Titulo\nContenido de prueba", encoding="utf-8")
    result = loaders.load_document(file_path)
    assert result["text"] == "# Titulo\n\nContenido de prueba"
    assert result["source"] == "note.md"
    assert result["title"] == "note"


def test_load_pdf_extracts_text_from_all_pages(tmp_path, monkeypatch):
    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, path):
            self.pages = [FakePage("Pagina uno"), FakePage("Pagina dos")]

    monkeypatch.setattr(loaders, "PdfReader", FakeReader)
    file_path = tmp_path / "doc.pdf"
    file_path.write_bytes(b"%PDF-1.4 fake")
    result = loaders.load_document(file_path)
    assert result["text"] == "Pagina uno\nPagina dos"
    assert result["source"] == "doc.pdf"


def test_load_docx_extracts_paragraph_text(tmp_path, monkeypatch):
    class FakeParagraph:
        def __init__(self, text):
            self.text = text

    class FakeDocxDocument:
        def __init__(self, path):
            self.paragraphs = [FakeParagraph("Primer parrafo"), FakeParagraph("Segundo parrafo")]

    monkeypatch.setattr(loaders, "DocxDocument", FakeDocxDocument)
    file_path = tmp_path / "doc.docx"
    file_path.write_bytes(b"fake docx bytes")
    result = loaders.load_document(file_path)
    assert result["text"] == "Primer parrafo\nSegundo parrafo"


def test_load_document_raises_on_unsupported_extension(tmp_path):
    file_path = tmp_path / "doc.xyz"
    file_path.write_text("data")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        loaders.load_document(file_path)
