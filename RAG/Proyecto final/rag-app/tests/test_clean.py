from app.clean import clean_text, drop_lines, find_boilerplate


def test_removes_invisible_chars_emojis_urls_and_extra_spaces():
    raw = "Despu\u00e9s\u200b  de   ba\u00f1ar \U0001F393 sus cuerpos. https://x.org/a\n\U0001F393\nOtra l\u00ednea."
    assert clean_text(raw) == "Despu\u00e9s de ba\u00f1ar sus cuerpos.\n\nOtra l\u00ednea."


def test_joins_hyphenated_line_breaks():
    assert clean_text("una pala-\nbra partida") == "una palabra partida"


def test_drops_page_numbers_and_repeated_headers():
    body = "\n".join(f"Cabecera del libro\nP\u00e1rrafo n\u00famero {i} con texto.\n{i}" for i in range(5))
    assert clean_text(body) == "\n\n".join(f"P\u00e1rrafo n\u00famero {i} con texto." for i in range(5))


def test_drops_menu_runs_but_keeps_single_heading():
    raw = "Dioniso\nDem\u00e9ter\nApolo\nHermes\nCuerpo largo, con texto.\nInvocaci\u00f3n a las musas\nOtro cuerpo, largo."
    assert clean_text(raw) == "Cuerpo largo, con texto.\n\nInvocaci\u00f3n a las musas\n\nOtro cuerpo, largo."


def test_strips_line_numbers_only_when_most_lines_use_them():
    numbered = "(1) Uno, dos.\n(5) Tres, cuatro.\nSin numero, aqui."
    assert clean_text(numbered) == "Uno, dos.\n\nTres, cuatro.\n\nSin numero, aqui."
    mostly_plain = "Texto normal, uno.\nTexto normal, dos.\n1.2 Introducci\u00f3n al tema, breve."
    assert "1.2 Introducci\u00f3n" in clean_text(mostly_plain)


def test_notes_are_kept_when_nothing_marks_them_as_noise():
    raw = "Cuerpo del texto, largo.\nNotas\n(1) Una nota, corta."
    assert "Una nota, corta." in clean_text(raw)


def test_boilerplate_is_lines_shared_by_three_or_more_documents():
    ad = "Suscr\u00edbete gratis, no te lo pierdas."
    docs = [clean_text(f"Contenido propio n\u00famero {i}, distinto.\n{ad}") for i in range(3)]
    boilerplate = find_boilerplate(docs)
    assert boilerplate == {ad}
    assert drop_lines(docs[0], boilerplate) == "Contenido propio n\u00famero 0, distinto."


def test_no_boilerplate_with_fewer_than_three_documents():
    docs = [clean_text("Igual en ambos, siempre.") for _ in range(2)]
    assert find_boilerplate(docs) == frozenset()


def test_keeps_only_text_between_start_and_end_markers():
    raw = "Cabecera\n*** START OF THE EBOOK X ***\nCuerpo del texto, largo.\n*** END OF THE EBOOK X ***\nPie legal"
    assert clean_text(raw) == "Cuerpo del texto, largo."


def test_without_markers_nothing_is_cut():
    assert clean_text("Uno, dos.\nTres, cuatro.") == "Uno, dos.\n\nTres, cuatro."


def test_drops_editorial_illustration_marks():
    raw = "Antes.\n[Ilustraci\u00f3n:\n\npie de foto largo]\nDespu\u00e9s [Illustration] del texto, largo."
    assert clean_text(raw) == "Antes.\n\nDespu\u00e9s del texto, largo."


def test_drops_table_of_contents_lines_but_not_sentences_with_numbers():
    raw = "XII.--Las Sirenas y Escila. 162\nPR\u00d3LOGO. VII\nUlises naveg\u00f3 durante 10 a\u00f1os por el mar."
    assert clean_text(raw) == "Ulises naveg\u00f3 durante 10 a\u00f1os por el mar."
