# FS Intelligence Dashboard

Monorepo for **FS Intelligence Dashboard**: earnings call transcripts (EarningsCall API), Federal Register regulatory monitoring, company regulatory profiles, and LLM analysis (Claude) — stored in SQLite for local development.

## Repo layout

- `backend/`: FastAPI API (Swagger at `/docs`)
- `frontend/`: Next.js UI

## Quickstart (local dev)

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs`.

### 2) Frontend

```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Environment variables

See `.env.example`.

