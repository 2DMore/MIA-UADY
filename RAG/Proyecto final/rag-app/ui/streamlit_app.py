import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG del curso MIA", page_icon="🌴", layout="wide")

MINIMAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.stApp {
    background-color: #ffffff;
    background-image:
        linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
        linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
        linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
    background-size: 44px 44px;
    background-position: 0 0, 0 22px, 22px -22px, -22px 0px;
    background-attachment: fixed;
}

html, body, [class*="css"], p, span, label, li {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important;
    font-size: 17px !important;
    color: #1a1a1a !important;
}

h1, h2, h3 {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif !important;
    font-weight: 700 !important;
    color: #111111 !important;
    letter-spacing: -0.5px;
    border-bottom: 2px solid #111111;
    padding-bottom: 6px;
}

[data-testid="stSidebar"] {
    background-color: #fafafa;
    border-right: 2px solid #111111;
}

[data-testid="stSidebar"] * {
    color: #1a1a1a !important;
}

[data-testid="stHeader"] {
    background-color: #ffffff !important;
    border-bottom: 2px solid #111111;
}

[data-testid="stDecoration"] {
    background-image: none !important;
    background-color: #111111 !important;
}

/* Streamlit's own chrome icons: sidebar collapse/expand arrow, header menu/deploy icons.
   Only recolor the icon itself, no background/border box. */
[data-testid="stHeader"] svg,
[data-testid="stToolbar"] svg,
[data-testid="stToolbarActions"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
    fill: #111111 !important;
    color: #111111 !important;
    opacity: 1 !important;
}

.stButton>button,
[data-testid="stFormSubmitButton"] button {
    background-color: #111111 !important;
    border: 2px solid #111111 !important;
    border-radius: 0px !important;
    box-shadow: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.5px;
    transition: all 0.15s ease-in-out;
}

.stButton>button,
.stButton>button *,
[data-testid="stFormSubmitButton"] button,
[data-testid="stFormSubmitButton"] button * {
    color: #ffffff !important;
    background-image: none !important;
    border: none;
}

.stButton>button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background-color: #ffffff !important;
    border: 2px solid #111111 !important;
}

.stButton>button:hover,
.stButton>button:hover *,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stFormSubmitButton"] button:hover * {
    color: #111111 !important;
}

.stButton>button:disabled,
[data-testid="stFormSubmitButton"] button:disabled {
    background-color: #d0d0d0 !important;
    border: 2px solid #888888 !important;
}

.stButton>button:disabled,
.stButton>button:disabled *,
[data-testid="stFormSubmitButton"] button:disabled,
[data-testid="stFormSubmitButton"] button:disabled * {
    color: #666666 !important;
}

[data-testid="stSidebar"] .stButton>button {
    border: 2px solid #111111 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
}

.stTextInput>div>div>input {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border: 2px solid #111111 !important;
    border-radius: 0px;
    font-family: 'Inter', sans-serif !important;
    font-size: 17px !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: #ffffff !important;
    border: 2px dashed #111111 !important;
    border-radius: 0px !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #1a1a1a !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background-color: #ffffff !important;
    border: 2px solid #111111 !important;
    border-radius: 0px !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button * {
    color: #111111 !important;
    background-image: none !important;
    border: none;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background-color: #111111 !important;
    border: 2px solid #111111 !important;
}

[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover * {
    color: #ffffff !important;
}

[data-testid="stFileUploaderFile"] {
    background-color: #fafafa !important;
    border: 1px solid #111111 !important;
    border-radius: 0px !important;
}

[data-testid="stFileUploaderFile"] * {
    color: #1a1a1a !important;
}

.streamlit-expanderHeader {
    background-color: #fafafa !important;
    color: #111111 !important;
    border: 1px solid #111111 !important;
    font-family: 'Inter', sans-serif !important;
}

hr {
    border-color: #111111 !important;
}
</style>
"""
st.markdown(MINIMAL_CSS, unsafe_allow_html=True)

st.title("RAG del curso MIA")


def fetch_health():
    try:
        response = httpx.get(f"{API_URL}/health", timeout=10)
        response.raise_for_status()
        return response.json(), None
    except httpx.HTTPError as exc:
        return None, str(exc)


with st.sidebar:
    st.header("Documentos indexados")
    health, health_error = fetch_health()
    if health_error:
        st.error(f"No se pudo conectar a la API: {health_error}")
    elif not health["sources"]:
        st.info("Aun no has ingestado documentos.")
    else:
        st.caption(f"{health['indexed_chunks']} chunks en {len(health['sources'])} documentos")
        for item in health["sources"]:
            st.write(f"- {item['source']} ({item['chunks']} chunks)")

    st.header("Cargar documentos")
    uploaded_files = st.file_uploader(
        "Selecciona PDF, Markdown o Word",
        type=["pdf", "md", "txt", "docx"],
        accept_multiple_files=True,
    )
    if st.button("Ingestar", disabled=not uploaded_files):
        total = len(uploaded_files)
        progress = st.progress(0)
        status = st.empty()
        documents_indexed = 0
        chunks_indexed = 0
        errors = []
        for i, uploaded_file in enumerate(uploaded_files, start=1):
            status.write(f"Indexando {uploaded_file.name} ({i}/{total})...")
            try:
                response = httpx.post(
                    f"{API_URL}/ingest",
                    files={"files": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")},
                    timeout=120,
                )
                response.raise_for_status()
                body = response.json()
                documents_indexed += body["documents_indexed"]
                chunks_indexed += body["chunks_indexed"]
                errors.extend(body["errors"])
            except httpx.HTTPError as exc:
                errors.append({"file": uploaded_file.name, "error": str(exc)})
            progress.progress(i / total)
        status.write("Ingesta completa.")
        st.success(f"Indexados {documents_indexed} documentos, {chunks_indexed} chunks.")
        if errors:
            st.warning(f"Errores: {errors}")
        st.rerun()

st.header("Preguntar")
with st.form(key="query_form", clear_on_submit=False):
    question = st.text_input("Escribe tu pregunta")
    submitted = st.form_submit_button("Enviar pregunta")

if submitted:
    if not question.strip():
        st.warning("Escribe una pregunta antes de enviar.")
    else:
        try:
            response = httpx.post(f"{API_URL}/query", json={"question": question}, timeout=60)
            response.raise_for_status()
            body = response.json()
            if body["abstained"]:
                st.info(body["answer"])
            else:
                st.markdown(f"### Respuesta\n{body['answer']}")
                st.markdown("### Citas")
                for i, citation in enumerate(body["citations"], start=1):
                    with st.expander(f"[{i}] {citation['source']} (score: {citation['score']:.2f})"):
                        st.write(citation["text"])
        except httpx.HTTPError as exc:
            st.error(f"No se pudo conectar a la API: {exc}")
        except KeyError:
            st.error("Respuesta inesperada de la API.")
