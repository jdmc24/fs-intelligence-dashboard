# Deploy: Railway (API) + Vercel (UI)

The **backend** is a long‑running FastAPI app (SQLite, optional scheduler). The **frontend** is Next.js. Deploy the API on **Railway** and the static/SSR app on **Vercel**, then point the UI at the API with public env vars.

## 1. Railway — backend

1. Create a project at [railway.app](https://railway.app) and **New service** → **GitHub repo** → select `fs-intelligence-dashboard`.
2. Open the service → **Settings** → **Root Directory** → set to **`backend`**.
3. **Build**: The repo includes **`backend/Dockerfile`** and **`backend/railway.toml`** so Railway uses **Dockerfile** builds (avoids “Error creating build plan with Railpack” on monorepos). Leave **Start Command** empty unless you override the image `CMD`.
4. **Variables** — add (use strong values for production):

   | Variable | Notes |
   |----------|--------|
   | `SEC_USER_AGENT` | Required. e.g. `FSIntelligenceDashboard/1.0 (contact: you@example.com)` |
   | `API_BEARER_TOKEN` | Required. Long random string; **must match** `NEXT_PUBLIC_API_BEARER_TOKEN` on Vercel. |
   | `ANTHROPIC_API_KEY` | For regulatory enrichment (optional if you only use transcripts). |
   | `ANTHROPIC_MODEL` | Optional; default in code is `claude-sonnet-4-6`. |
   | `EARNINGSCALL_API_KEY` | Optional; needed for tickers beyond demo tier. |
   | `DATABASE_URL` | Default SQLite path is `./data/app.db` under `backend`. For persistence across deploys, add a **Volume** (see below). |
   | `REGULATORY_SCHEDULER_ENABLED` | Default `false`. Set `true` only if you want in-process ingest/enrich on an interval (uses API keys + cost). |

5. **Networking** → **Generate Domain** (or attach a custom domain). Copy the public URL, e.g. `https://your-api.up.railway.app`.
6. Smoke test: `GET https://your-api.up.railway.app/healthz` → `{"ok":true}` with no auth.  
   `GET /docs` should load Swagger with title **FS Intelligence Dashboard API**.

### SQLite persistence on Railway

The default DB path is on the container filesystem and **can reset** when the service redeploys. To keep data:

- Add a **Volume** in Railway mounted e.g. at `/data`, then set:
  - `DATABASE_URL=sqlite+aiosqlite:////data/app.db`  
  (four slashes after `sqlite+aiosqlite:` for an absolute path.)

## 2. Vercel — frontend

1. Import the same GitHub repo at [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. **Root Directory** → **`frontend`** (important).
3. **Environment Variables** (Production — and Preview if you want):

   | Name | Value |
   |------|--------|
   | `NEXT_PUBLIC_BACKEND_URL` | Your Railway public API URL, e.g. `https://your-api.up.railway.app` (no trailing slash). |
   | `NEXT_PUBLIC_API_BEARER_TOKEN` | **Same** string as Railway `API_BEARER_TOKEN`. |

4. Deploy. Open the Vercel URL; the app will call the Railway API from the browser (CORS is open in the API).

## 3. Checklist

- [ ] Railway: `API_BEARER_TOKEN` set  
- [ ] Vercel: `NEXT_PUBLIC_BACKEND_URL` + `NEXT_PUBLIC_API_BEARER_TOKEN` match Railway  
- [ ] Optional: volume + `DATABASE_URL` if you need durable SQLite  

## 4. Local `.env` unchanged

Developers still copy `.env.example` → `backend/.env` and `frontend/.env.local` for local runs; production uses only the host env vars above.
