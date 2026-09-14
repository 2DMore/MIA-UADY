# RAG del curso MIA

Sistema RAG (Streamlit + FastAPI + ChromaDB + Google AI) sobre 7 PDFs
teoricos del curso (busqueda, perceptron multicapa, vision computacional).

## Setup

1. `python -m venv venv && ./venv/Scripts/pip install -r requirements.txt`
2. Copia `.env.example` a `.env` y coloca tu clave de
   [Google AI Studio](https://aistudio.google.com/apikey) en `GOOGLE_API_KEY`.
3. Ajusta `MIN_SCORE` en `.env` si lo recalibras (ver seccion Abstencion).

## Levantar el sistema

Terminal 1:
```
uvicorn app.main:app --reload --port 8000
```

Terminal 2:
```
streamlit run ui/streamlit_app.py
```

Abre `http://localhost:8501`, sube los PDFs de `data/` desde la barra
lateral y pulsa "Ingestar". Luego escribe una pregunta.

## Probar la API directamente

```
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" \
  -d '{"question": "Que es la busqueda en anchura (BFS)?"}'
```

O usa `http://localhost:8000/docs` (Swagger UI) — expone `/health`,
`/ingest` y `/query`.

## Corpus

7 PDFs en `data/` (101 chunks indexados con la configuracion de chunking
actual): `chapter03.pdf`, `chapter04a.pdf`, `01_Linear_Regression.pdf`,
`02_Classification.pdf`, `03_Neural_Networks.pdf`, `01 CNN intro.pdf`,
`02 CNN architectures.pdf`. Tema coherente: fundamentos de IA/ML del curso
(busqueda, perceptron multicapa, vision computacional).

## Chunking

300 palabras por chunk, 60 de solape (punto medio del rango sugerido de
200-400 palabras / 40-80 de solape). Suficiente contexto por chunk sin
diluir la relevancia semantica.

## Abstencion

Umbral de score minimo (`MIN_SCORE=0.60` en `.env`). Si el mejor chunk
recuperado tiene score (similitud coseno) menor a `MIN_SCORE`, el sistema
responde "No tengo evidencia suficiente..." sin llamar a Gemini.

Scores observados durante la calibracion (script
`scripts/calibrate_min_score.py`, corpus completo indexado):

| Pregunta | best_score | Tipo |
|---|---|---|
| Que es la busqueda en anchura (BFS)? | 0.636 | dominio |
| Que es una funcion de activacion en una red neuronal? | 0.683 | dominio |
| Que es una capa convolucional? | 0.687 | dominio |
| Que dice el material sobre los Transformers y los LLMs? | 0.579 | fuera de dominio (tematicamente cercano) |
| Cual es la capital de Francia? | 0.481 | fuera de dominio (control, sin relacion) |
| Como se prepara una paella valenciana? | 0.483 | fuera de dominio (control, sin relacion) |

`MIN_SCORE=0.60` se eligio en el punto medio entre la pregunta de dominio
mas baja (0.636) y el caso fuera-de-dominio mas dificil (0.579, Transformers,
tematicamente cercano a redes neuronales). Nota: el margen entre ambos casos
es estrecho (0.057); preguntas de dominio muy genericas podrian, en teoria,
acercarse al umbral. Los casos de control claramente ajenos al dominio
(capital de Francia, paella) quedan muy por debajo (~0.48), con margen
amplio.

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

## Verificacion realizada

- Suite automatizada: 25/25 tests pasando (`pytest`), sin llamadas de red
  (loaders, chunk, embed, generate, store con fakes; main.py con
  monkeypatching de los clientes).
- Ingesta real de los 7 PDFs via `/ingest`: `documents_indexed=7`,
  `chunks_indexed=101`, `errors=[]`.
- 3 preguntas de dominio via `/query`: respuestas en espanol, con citas
  `[n]` y chunks/scores visibles.
- 1 pregunta imposible (Transformers/LLMs) via `/query`: `abstained=true`,
  sin citas, sin alucinar.
- Reinicio de la API: el conteo de chunks indexados se mantuvo en 101
  (persistencia de Chroma confirmada).
- `GET /docs` / `openapi.json` lista `/health`, `/ingest`, `/query`.
