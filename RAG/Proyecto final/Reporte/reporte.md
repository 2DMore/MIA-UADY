# Reporte — Sistema RAG de mitología y literatura clásica

Alumno: Oscar Daniel Moreno Flores

Fecha de Entrega: 04/10/2026

## Dominio y tamaño del corpus

Mitología y literatura clásica grecolatina: 5 obras de dominio público
(tragedia griega y poesía de Ovidio), tomadas de Project Gutenberg
(fuentes y traductores en [../corpus/FUENTES.md](../corpus/FUENTES.md)).

| Archivo | Obra | Palabras limpias | Chunks |
|---|---|---|---|
| `esquilo_tragedias.txt` | Esquilo, *Tragedias* | 72.999 | 304 |
| `sofocles_tragedias_tebanas.txt` | Sofocles, *Edipo rey; Edipo en Colona; Antigona* | 39.708 | 166 |
| `ovidio_metamorfoseos_1.txt` | Ovidio, *Metamorfoseos* (tomo 1 de 4) | 33.285 | 139 |
| `ovidio_amores.txt` | Ovidio, *Amores* | 28.277 | 118 |
| `ovidio_arte_de_amar.txt` | Ovidio, *El arte de amar* | 23.823 | 100 |

Total: ~198.000 palabras, 827 chunks. Modelo de embeddings:
`gemini-embedding-001` (mismo modelo para documentos y preguntas).
Salvedad: *Metamorfoseos* es solo el tomo 1 de 4 (libros I a III).

## Particiones

El corpus se particionó en chunks de 300 palabras con un solape de 60
palabras entre chunks consecutivos. Ambos valores se fijaron directamente en
el punto medio del rango sugerido (200-400 palabras de tamaño, 40-80 de
solape). El solape existe porque el corte
entre un chunk y el siguiente puede caer en medio de un diálogo o de una
idea, dado que el corpus incluye obras de teatro y poesía; al repetir las
últimas 60 palabras de un chunk como inicio del siguiente, ese fragmento de
contexto no se pierde en el chunk que sigue, aunque el corte en sí no se
evita. Antes de partir el texto, `app/clean.py` quita ruido genérico propio
de la descarga de Gutenberg (números de página, índices, marcadores
editoriales, líneas repetidas entre documentos del corpus) para que los
chunks no incluyan ruido.

## Criterios para abstenerse

El sistema se abstiene cuando el score (similitud coseno) del mejor chunk
recuperado queda por debajo de un umbral mínimo, `MIN_SCORE=0.65`. Ese
umbral se calibró probando 5 preguntas: tres de dominio, para verificar que
el sistema recuperaba y respondía correctamente (Prometeo 0.726, Edipo
0.755, Narciso 0.797), y dos fuera de dominio, cada una probando un
escenario distinto — una totalmente ajena al corpus (capital de Francia,
0.567) y otra deliberadamente parecida por tratarse también de mitología,
pero de otra tradición (Odín y la mitología nórdica, 0.581), para comprobar
que el sistema no se confunde por similitud temática. El umbral se fijó en
el punto medio entre el score de dominio más bajo y el score fuera de
dominio más alto.

El margen resultante (0.145) es angosto porque la calibración se hizo con una muestra chica (solo 3 preguntas de dominio): una pregunta de dominio muy amplia o genérica podría caer por debajo del umbral y provocar una abstención indebida, aunque el corpus sí tuviera la información.

## Qué sale de Google AI y qué hace Chroma

De Google AI se cuenta con dos modelos separados, que se usan en momentos distintos del flujo. El modelo de embeddings (`gemini-embedding-001`) convierte texto en un vector numérico: se usa dos veces, una al ingerir cada chunk del corpus (que queda guardado en Chroma con su vector) y otra al hacer una pregunta. No redacta nada, solo cambia la entrada por una representación matemática, que en este caso son vectores. Se buscó que ambos usos —chunks y preguntas— compartan el mismo modelo, porque el paso siguiente compara esos vectores por similitud coseno; si vinieran de modelos distintos, la comparación no tendría sentido.

Chroma no calcula ningún vector propio: recibe explícitamente los embeddings de Google AI en `add` y `query`, nunca usa su embedder por defecto. Con el vector de la pregunta ya calculado, lo compara contra los vectores de los chunks que tiene almacenados y devuelve los `top_k` más cercanos: esta es la recuperación, el paso que da nombre a RAG.

Por último, el segundo modelo de Google AI, el de generación (`gemini-3.6-flash`), es el que recibe la pregunta junto con los chunks ya recuperados por Chroma y redacta la respuesta final en español, citando `[n]`; no busca nada, se encarga de escribir con la evidencia que ya se le entregó.

