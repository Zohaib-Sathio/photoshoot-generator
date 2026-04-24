FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Pillow runtime libs (JPEG + PNG decoding for Gemini reference images)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py image_generator.py prompts.py ./
COPY static ./static

# Non-root user + persistent data dirs
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app/uploads /app/outputs \
    && chown -R app:app /app
USER app

EXPOSE 8000

# Production server — no --reload. Mount .env at runtime for the API keys.
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
