# RAG de mitologia y literatura clasica

Sistema RAG (Streamlit + FastAPI + ChromaDB + Google AI) sobre 5 textos en
espanol de tragedia griega y poesia de Ovidio, tomados de Project Gutenberg.

## Setup

1. `python -m venv venv && ./venv/Scripts/pip install -r requirements.txt`
2. Copia `.env.example` a `.env` y coloca tu clave de
   [Google AI Studio](https://aistudio.google.com/apikey) en `GOOGLE_API_KEY`.
3. Ajusta `MIN_SCORE` en `.env` (ver seccion Abstencion).

## Levantar el sistema

Terminal 1:
```
uvicorn app.main:app --reload --port 8000
```

Terminal 2:
```
streamlit run ui/streamlit_app.py
```

Abre `http://localhost:8501`, sube los `.txt` de `data/` desde la barra
lateral y pulsa "Ingestar". Luego escribe una pregunta.

Para que la limpieza detecte lineas repetidas entre documentos (ver Limpieza),
los archivos deben estar en `data/` antes de ingerir; suben desde ahi.

## Probar la API directamente

```
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" \
  -d '{"question": "Quien era Prometeo y por que fue castigado?"}'
```

O usa `http://localhost:8000/docs` (Swagger UI) — expone `/health`,
`/ingest` y `/query`.

## Corpus

5 obras completas de dominio publico en `data/` (fuentes, traductores y
enlaces en [data/FUENTES.md](data/FUENTES.md)):

| Archivo | Obra | Palabras limpias | Chunks |
|---|---|---|---|
| `esquilo_tragedias.txt` | Esquilo, *Tragedias* | 72.999 | 304 |
| `sofocles_tragedias_tebanas.txt` | Sofocles, *Edipo rey; Edipo en Colona; Antigona* | 39.708 | 166 |
| `ovidio_metamorfoseos_1.txt` | Ovidio, *Metamorfoseos* (tomo 1 de 4) | 33.285 | 139 |
| `ovidio_amores.txt` | Ovidio, *Amores* | 28.277 | 118 |
| `ovidio_arte_de_amar.txt` | Ovidio, *El arte de amar* | 23.823 | 100 |

Total: unas 198.000 palabras, 827 chunks (calculados con `chunk_text` sobre el
texto ya limpio). Tema: mitologia y literatura clasica grecolatina. Los
`.txt` son la descarga original de Gutenberg; los textos son de dominio
publico y se usan sin fines comerciales, con fines academicos.

Salvedad: *Metamorfoseos* es solo el tomo 1 de 4 (libros I a III), no la obra
completa.

## Limpieza

`app/clean.py` limpia los `.txt` y `.md` antes de partirlos en chunks. Las
reglas son genericas, no dependen del sitio de origen:

- Caracteres invisibles, emojis, URLs, guiones de fin de linea y espacios.
- Numeros de pagina y cabeceras o pies repetidos dentro del documento.
- Indices y menus (rachas de lineas cortas sin puntuacion) y lineas de tabla
  de contenido (texto que termina en numero de pagina).
- Marcadores editoriales como `[Illustration]`.
- Delimitadores `*** START ... ***` / `*** END ... ***`: solo se conserva el
  texto entre ellos (si existen).
- Numeracion de versos o parrafos, solo si la usa la mayoria del documento.
- Lineas identicas en 3 o mas documentos del corpus (avisos legales, menus):
  `/ingest` las detecta sobre los archivos de `data/` y las quita.

No se pasa a minusculas ni se quitan stopwords o puntuacion: eso solo tiene
sentido con bolsa de palabras (`RAG/project/rag/tokenize.py`); los embeddings
de Google AI usan el texto natural. Del curso se reutiliza la normalizacion de
espacios y el troceo por palabras completas con solape.

Quedan sin limpiar: las notas del transcriptor al inicio de cada libro y
algunos indices finales con formato irregular. Son pocos parrafos.
PDF y docx no pasan por la limpieza.

## Chunking

300 palabras por chunk, 60 de solape (punto medio del rango sugerido de
200-400 palabras / 40-80 de solape). Suficiente contexto por chunk sin
diluir la relevancia semantica.

## Abstencion

Umbral de score minimo (`MIN_SCORE` en `.env`). Si el mejor chunk recuperado
tiene score (similitud coseno) menor a `MIN_SCORE`, el sistema responde "No
tengo evidencia suficiente..." sin llamar a Gemini.

Scores observados en la calibracion (`scripts/calibrate_min_score.py`, corpus
completo de 827 chunks indexado):

| Pregunta | best_score | Tipo |
|---|---|---|
| Quien era Prometeo y por que fue castigado? | 0.726 | dominio |
| Que le ocurrio a Edipo cuando descubrio la verdad sobre su origen? | 0.755 | dominio |
| Que le paso a Narciso segun las Metamorfosis? | 0.797 | dominio |
| Quien es Odin y que papel tiene en Ragnarok? | 0.581 | fuera de dominio (mitologia nordica, cercana) |
| Cual es la capital de Francia? | 0.567 | fuera de dominio (control, sin relacion) |

`MIN_SCORE=0.65` se eligio en el punto medio entre la pregunta de dominio mas
baja (0.726) y el caso fuera-de-dominio mas alto (0.581, Odin). El margen entre
ambos es de 0.145. Con solo tres preguntas de dominio es una estimacion:
preguntas muy genericas del dominio podrian acercarse al umbral.

## Google AI: que hace cada modelo

- `gemini-embedding-001`: convierte cada chunk y cada pregunta en un
  vector (mismo modelo para ambos, para que el k-NN sea comparable).
- `gemini-3.6-flash`: genera la respuesta final en espanol, citando `[n]`,
  usando solo los chunks recuperados por ChromaDB. (Nota: la spec original
  sugeria `gemini-2.5-flash`, pero ese modelo dejo de estar disponible para
  nuevos usuarios durante el desarrollo; se uso el modelo vigente al momento
  de la entrega.)
- ChromaDB (`chromadb==1.5.9`): almacena chunks + vectores + metadatos de
  forma persistente (`chroma/`) y devuelve los `top_k` mas cercanos por
  similitud coseno (`hnsw:space=cosine`). Nota: la spec sugeria
  `chromadb==0.5.20`, pero esa version depende de compilar `chroma-hnswlib`
  desde codigo fuente en Windows/Python 3.13 (requiere Visual Studio Build
  Tools). La version 1.5.9 reescribio el nucleo en Rust con wheels
  precompilados y mantiene la misma API usada aqui (`PersistentClient`,
  `get_or_create_collection`, `add`, `query`).

## Verificacion

- Suite automatizada: 40 tests pasando (`pytest`), sin llamadas de red
  (loaders, limpieza, chunk, embed, generate, store con fakes; main.py con
  monkeypatching de los clientes).
- Calibracion de `MIN_SCORE` con el corpus nuevo: hecha (ver Abstencion).
- Ingesta real de los 5 `.txt` via `/ingest` (una sola peticion): `documents_indexed=5`,
  `chunks_indexed=827`, `errors=[]`, en unos 55 s.
- 3 preguntas de dominio via `/query` (Prometeo, Edipo, Narciso): respuestas en
  espanol con citas `[n]` que apuntan a chunks de `esquilo_tragedias.txt`,
  `sofocles_tragedias_tebanas.txt` y `ovidio_metamorfoseos_1.txt`, con scores
  de 0.70 a 0.80.
- 2 preguntas imposibles (Odin y Ragnarok; capital de Francia): `abstained=true`,
  sin citas, sin llamar a Gemini. Una pregunta en blanco tambien se abstiene.
- Reinicio de la API: el conteo se mantuvo en 827 chunks (persistencia de
  Chroma confirmada). El indice anterior (PDFs del curso) se aparto a
  `chroma_old_pdfs/` (en `.gitignore`).
- `GET /docs` responde 200 y `openapi.json` lista `/health`, `/ingest`, `/query`.
  CORS permite `http://localhost:8501`.
- **Pendiente:** evidencias visuales (capturas de Streamlit con citas y scores,
  la misma pregunta en `/docs`, y la pregunta fuera de dominio) y el reporte
  de una pagina.
