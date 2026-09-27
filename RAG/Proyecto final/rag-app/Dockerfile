FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY ui ./ui
COPY .streamlit ./.streamlit
COPY data ./data

EXPOSE 8000 8501
# El comando lo define docker-compose.yml (api o ui).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
