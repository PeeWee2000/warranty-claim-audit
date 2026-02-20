FROM python:3.13-slim

WORKDIR /app

# Install uv and system deps
RUN pip install --no-cache-dir uv

# Install Python dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache ".[ml]"

# Pre-download the embedding model at build time so startup is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY src/ src/

# Model artifacts are mounted via docker-compose volume
RUN mkdir -p /app/data/models

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
