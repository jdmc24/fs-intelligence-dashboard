"""One-time DB setup: ORM tables + regulatory FTS virtual table + company profile seed.

Schema is managed by `Base.metadata.create_all`, which is additive for new tables
but does NOT add missing columns to existing tables. `_ensure_additive_columns`
applies SQLite-safe ALTERs for columns introduced after launch so a redeployed
service with an existing volume picks them up without manual migration.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

import app.models  # noqa: F401 — register models with Base.metadata

from app.db import SessionLocal, engine
from app.models import Base
from app.services.regulations_db import ensure_reg_search_fts
from app.services.regulations_service import seed_company_profiles


_ADDITIVE_COLUMNS: list[tuple[str, str, str]] = [
    # (table, column, sqlite_type_decl)
    ("reg_enrichments", "tool_calls_json", "TEXT"),
]


async def _ensure_additive_columns(conn: AsyncConnection) -> None:
    for table, col, type_decl in _ADDITIVE_COLUMNS:
        result = await conn.execute(text(f"PRAGMA table_info({table})"))
        existing_cols = {row[1] for row in result.fetchall()}
        if col not in existing_cols:
            await conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {col} {type_decl}'))


async def init_platform_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_additive_columns(conn)
        await ensure_reg_search_fts(conn)


async def init_company_profiles() -> None:
    async with SessionLocal() as session:
        await seed_company_profiles(session)
