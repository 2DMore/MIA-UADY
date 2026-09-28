# Corpus de ejemplo

Copia de entrega del corpus usado por el sistema RAG (punto 2 de la entrega).
Es identico al contenido de `rag-app/data/`, que es la carpeta que la
aplicacion realmente lee (`DATA_PATH`) y desde la que se ingesto.

Ver [FUENTES.md](FUENTES.md) para el origen, traductor y enlace de descarga
de cada obra (Project Gutenberg, dominio publico).

| Archivo | Obra | Palabras limpias | Chunks |
|---|---|---|---|
| `esquilo_tragedias.txt` | Esquilo, *Tragedias* | 72.999 | 304 |
| `sofocles_tragedias_tebanas.txt` | Sofocles, *Edipo rey; Edipo en Colona; Antigona* | 39.708 | 166 |
| `ovidio_metamorfoseos_1.txt` | Ovidio, *Metamorfoseos* (tomo 1 de 4) | 33.285 | 139 |
| `ovidio_amores.txt` | Ovidio, *Amores* | 28.277 | 118 |
| `ovidio_arte_de_amar.txt` | Ovidio, *El arte de amar* | 23.823 | 100 |

Total: unas 198.000 palabras, 827 chunks. Detalles de limpieza y chunking en
[../rag-app/README.md](../rag-app/README.md).
