# Explicit image for Railway (avoids Railpack/Nixpacks auto-detect issues on monorepos).
FROM python:3.11-slim-bookworm

WORKDIR /app

# lxml (BeautifulSoup) needs libxml2/libxslt headers at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
# Railway sets PORT at runtime
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
