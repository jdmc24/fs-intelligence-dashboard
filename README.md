# Stock Intelligence Dashboard

Full-stack app for **public-equities research**: pull **earnings call transcripts**, monitor **Federal Register** regulatory activity, and run **LLM-backed analysis** (Anthropic Claude). Monorepo with a Next.js UI and FastAPI API; SQLite for a simple local data store.

| | |
|---|---|
| **Live app** | *Add your Vercel production URL (GitHub → repo **About** → Website).* |
| **API** | *Your Railway (or host) URL — OpenAPI/Swagger at `/docs`.* |
| **Source** | [github.com/jdmc24/stock-intelligence-dashboard](https://github.com/jdmc24/stock-intelligence-dashboard) |

## What it does

- **Earnings** — Fetch transcripts (EarningsCall API), store them, run structured analysis.
- **Regulations** — Ingest and browse regulatory items; company-facing regulatory angles.
- **Compare & search** — Cross-cut views over stored content (see app nav).

## Stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind.
- **Backend:** FastAPI, async SQLAlchemy, SQLite (`aiosqlite`) for dev/single-node deploys.
- **AI:** Anthropic API (configurable model).
- **Production (typical):** API on **Railway**, UI on **Vercel** — details in [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Repo layout

```
backend/    # FastAPI — `uvicorn app.main:app`
frontend/   # Next.js — `npm run dev`
```

## Local development

**1. Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env     # fill in keys; see comments in file
uvicorn app.main:app --reload --port 8000
```

Open [http://localhost:8000/docs](http://localhost:8000/docs).

**2. Frontend**

```bash
cd frontend
npm install
cp ../.env.example .env.local   # point NEXT_PUBLIC_BACKEND_URL at the API
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Configuration

All variables are documented in [`.env.example`](./.env.example). Minimum for meaningful local runs: backend secrets for **Anthropic**, **EarningsCall** (beyond demo tickers), and matching **`API_BEARER_TOKEN`** / **`NEXT_PUBLIC_API_BEARER_TOKEN`**.

## Deploy

**Railway** (API) + **Vercel** (frontend, root directory `frontend`): env vars, volumes, and ordering are in [`DEPLOYMENT.md`](./DEPLOYMENT.md). Viewers use the **live URLs** only; they do not need to deploy the repo.
