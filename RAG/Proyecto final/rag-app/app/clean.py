"""Limpieza generica de texto antes de partirlo en chunks.

Las notebooks y `project/` del curso hacen muy poca limpieza: normalizan el
espacio en blanco (`text.split()` + `" ".join`) y trocean en ventanas de
palabras completas con solape. Aqui se hace lo mismo y ademas se quita el
ruido que de otro modo acabaria en los chunks y en los embeddings.

Ninguna regla depende del sitio de origen. El ruido se detecta por lo que es:
  - caracteres invisibles, emojis, guiones de fin de linea, URLs, espacios;
  - numeros de pagina y cabeceras/pies repetidos dentro del documento;
  - indices y menus: rachas de lineas cortas sin puntuacion;
  - numeracion de versos o parrafos, solo si la usa la mayoria del documento;
  - lineas de tabla de contenido (texto seguido de un numero de pagina) y
    marcadores editoriales como "[Ilustracion: ...]";
  - delimitadores de texto `*** START ... ***` / `*** END ... ***`: se conserva
    solo lo que hay entre ellos (si existen);
  - lineas identicas en varios documentos del corpus (menus, anuncios,
    avisos legales): `find_boilerplate` las detecta y `drop_lines` las quita.

No se pasa a minusculas ni se quitan stopwords o puntuacion: eso solo tiene
sentido con bolsa de palabras (`project/rag/tokenize.py`). Los embeddings de
Google AI usan el texto natural.
"""
import re
import unicodedata
from collections import Counter

# Caracteres invisibles que trae el HTML y que parten palabras o suman tokens.
_INVISIBLE = re.compile("[​‌‍⁠﻿­]")
_CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿]")
_URL = re.compile(r"https?://\S+|www\.\S+")
_PAGE_NUMBER = re.compile(r"^(?:p[aá]g(?:ina)?\.?\s*)?\d{1,4}(?:\s*(?:/|de)\s*\d{1,4})?$", re.I)
_HYPHEN_BREAK = re.compile(r"(\w)-\n(\w+)")
_NOTE_REF = re.compile(r"\[\d+\]")  # referencias a notas: "[12]"
# Numeracion al inicio de linea: "(5) ", "1.2.3 ".
_LINE_NUMBER = re.compile(r"^(?:\(\d+\)|\d+(?:\.\d+){1,3})\s+")

# Marcadores editoriales: "[Illustration]", "[Ilustracion: pie de foto...]".
_EDITORIAL_MARK = re.compile(r"\[(?:Ilustraci[oó]n|Illustration)\b[^\]]*\]", re.I)
# Delimitadores del texto propiamente dicho.
_START_MARK = re.compile(r"^\*{3}\s*START\b.*\*{3}$", re.I)
_END_MARK = re.compile(r"^\*{3}\s*END\b.*\*{3}$", re.I)
# Entrada de indice: texto corto que termina en numero de pagina ("... 162",
# "PROLOGO. VII"), sin ser una frase completa.
_TOC_LINE = re.compile(r"^.{3,}?(?:\s\d{1,4}|\.\s+[IVXLC]{1,6})$")
_TOC_MAX_WORDS = 20

_REPEAT_MIN = 4  # veces que se repite una cabecera/pie dentro de un documento
_REPEAT_MAX_WORDS = 12
_MENU_MAX_WORDS = 6  # una linea de menu es corta y no tiene puntuacion
_MENU_RUN_MIN = 3  # rachas de lineas de menu seguidas que se descartan
_NUMBERED_SHARE = 0.5  # fraccion de lineas numeradas para quitar la numeracion
_BOILERPLATE_MIN_DOCS = 3  # documentos distintos que comparten una linea


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n"))
    text = _INVISIBLE.sub("", _CONTROL.sub("", text)).replace("\xa0", " ")
    return _HYPHEN_BREAK.sub(r"\1\2", text)


def _is_menu_item(line: str) -> bool:
    return len(line.split()) <= _MENU_MAX_WORDS and not re.search(r"[.,;:!?¡¿]", line)


def _drop_menu_runs(lines: list[str]) -> list[str]:
    """Quita rachas de lineas cortas seguidas; un titulo suelto se conserva."""
    kept: list[str] = []
    run: list[str] = []
    for line in lines + [""]:
        if line and _is_menu_item(line):
            run.append(line)
            continue
        if len(run) < _MENU_RUN_MIN:
            kept.extend(run)
        run = []
        if line:
            kept.append(line)
    return kept


def _strip_envelope(lines: list[str]) -> list[str]:
    """Si hay marcas START/END, conserva solo el texto que queda entre ellas."""
    stripped = [line.strip() for line in lines]
    start = next((i for i, l in enumerate(stripped) if _START_MARK.match(l)), None)
    end = next((i for i, l in enumerate(stripped) if _END_MARK.match(l)), None)
    return lines[(start + 1 if start is not None else 0):(end if end is not None else len(lines))]


def _lines(text: str) -> list[str]:
    lines = []
    text = _EDITORIAL_MARK.sub("", _normalize(text))
    for raw in _strip_envelope(text.splitlines()):
        had_emoji = bool(_EMOJI.search(raw))
        line = _URL.sub("", _EMOJI.sub("", raw))
        line = re.sub(r"\s+", " ", line).strip()
        if not line and had_emoji:
            continue  # linea que solo era un adorno
        if not line or _PAGE_NUMBER.match(line):
            continue
        if len(line.split()) <= _TOC_MAX_WORDS and _TOC_LINE.match(line):
            continue
        lines.append(line)
    return lines


def clean_text(text: str) -> str:
    lines = _lines(text)

    counts = Counter(lines)
    lines = [
        line for line in lines
        if not (counts[line] >= _REPEAT_MIN and len(line.split()) <= _REPEAT_MAX_WORDS)
    ]

    lines = [_NOTE_REF.sub("", line).strip() for line in lines]
    numbered = sum(1 for line in lines if _LINE_NUMBER.match(line))
    if lines and numbered / len(lines) >= _NUMBERED_SHARE:
        lines = [_LINE_NUMBER.sub("", line) for line in lines]

    return "\n\n".join(_drop_menu_runs([line for line in lines if line]))


def find_boilerplate(texts: list[str]) -> frozenset[str]:
    """Lineas identicas en varios documentos: menus, anuncios, avisos legales.

    Un texto propio no se repite literalmente entre documentos distintos;
    el ruido de la pagina de origen si.
    """
    seen: Counter[str] = Counter()
    for text in texts:
        seen.update(set(text.split("\n\n")))
    return frozenset(
        line for line, n in seen.items() if n >= _BOILERPLATE_MIN_DOCS and line.strip()
    )


def drop_lines(text: str, boilerplate: frozenset[str]) -> str:
    if not boilerplate:
        return text
    return "\n\n".join(p for p in text.split("\n\n") if p not in boilerplate)
