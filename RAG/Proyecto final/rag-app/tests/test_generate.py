from app.generate import Generator, build_prompt, ABSTENTION_MESSAGE, GENERATION_MODEL


def test_build_prompt_numbers_chunks_and_includes_question():
    chunks = [
        {"source": "a.pdf", "text": "texto A"},
        {"source": "b.pdf", "text": "texto B"},
    ]
    prompt = build_prompt("Que es X?", chunks)
    assert "[1] (fuente: a.pdf) texto A" in prompt
    assert "[2] (fuente: b.pdf) texto B" in prompt
    assert "Que es X?" in prompt


def test_generate_returns_abstention_message_when_no_chunks():
    generator = Generator(client=object())
    assert generator.generate("pregunta", []) == ABSTENTION_MESSAGE


def test_generate_calls_client_with_built_prompt_and_returns_text():
    class FakeResponse:
        text = "Respuesta anclada [1]."

    class FakeModels:
        def __init__(self):
            self.last_call = None

        def generate_content(self, model, contents):
            self.last_call = (model, contents)
            return FakeResponse()

    class FakeClient:
        def __init__(self):
            self.models = FakeModels()

    fake_client = FakeClient()
    generator = Generator(client=fake_client)
    result = generator.generate("Que es X?", [{"source": "a.pdf", "text": "texto A"}])
    assert result == "Respuesta anclada [1]."
    model, prompt = fake_client.models.last_call
    assert model == GENERATION_MODEL
    assert "texto A" in prompt
