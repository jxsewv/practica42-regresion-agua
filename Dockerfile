FROM python:3.11-slim

# Hugging Face / servidores propios: el contenedor corre con el usuario 1000
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" \
    MPLCONFIGDIR=/tmp/matplotlib \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Capa aparte para lo nuevo: reutiliza la caché de la capa anterior (build rápido)
COPY --chown=user requirements-extra.txt requirements-extra.txt
RUN pip install --no-cache-dir -r requirements-extra.txt

COPY --chown=user . /app

EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.enableWebsocketCompression=false"]
