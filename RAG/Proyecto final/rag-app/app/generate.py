import os

from google import genai

GENERATION_MODEL = "gemini-3.6-flash"
ABSTENTION_MESSAGE = "No tengo evidencia suficiente en el corpus para responder esa pregunta."


class GenerationError(RuntimeError):
    pass


def _default_client():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise GenerationError("GOOGLE_API_KEY is not set")
    return genai.Client(api_key=api_key)


def build_prompt(question: str, chunks: list[dict]) -> str:
    evidence = "\n\n".join(
        f"[{i + 1}] (fuente: {c['source']}) {c['text']}" for i, c in enumerate(chunks)
    )
    return (
        "Responde la pregunta en espanol usando EXCLUSIVAMENTE la evidencia numerada.\n"
        "Cita las fuentes usando [n]. Si la evidencia no cubre la pregunta, dilo "
        "explicitamente en vez de inventar una respuesta.\n\n"
        f"Evidencia:\n{evidence}\n\nPregunta: {question}\nRespuesta:"
    )


class Generator:
    def __init__(self, client=None, model: str = GENERATION_MODEL):
        self._client = client
        self._model = model

    @property
    def client(self):
        if self._client is None:
            self._client = _default_client()
        return self._client

    def generate(self, question: str, chunks: list[dict]) -> str:
        if not chunks:
            return ABSTENTION_MESSAGE
        prompt = build_prompt(question, chunks)
        response = self.client.models.generate_content(model=self._model, contents=prompt)
        return response.text
