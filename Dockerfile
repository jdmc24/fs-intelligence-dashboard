# Monorepo root Dockerfile — used when Railway’s “Root Directory” is the repository root
# (empty or `/`). Railway then finds this file and builds the FastAPI app from ./backend.
#
# Recommended: set Service → Settings → Root Directory to `backend` so only backend files
# are sent to the builder; then Railway uses backend/Dockerfile instead (smaller context).

FROM python:3.11-slim-bookworm

WORKDIR /app

# Native libs needed to compile/use lxml (BeautifulSoup stack)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (path is relative to repo root build context)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application package lives under backend/
COPY backend/ .

ENV PYTHONUNBUFFERED=1
# Railway injects PORT at runtime
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
