# AcuGrade AI — Backend

Python/Flask backend for the AcuGrade adaptive learning & assessment
platform. See `/frontend` for the React app this serves, and
`docs/FRONTEND_BACKEND_MAPPING.md` for how the two are wired together.

## Stack
Flask · SQLAlchemy · MySQL (PyMySQL) · Pydantic · PyJWT · bcrypt ·
Mistral API · ChromaDB (optional) · ArangoDB (optional)

## Local setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: at minimum set DATABASE_URL and JWT_SECRET_KEY.
# MISTRAL_API_KEY is optional — without it, every AI call automatically
# uses its deterministic fallback path (see docs/ARCHITECTURE.md).
```

### Database
```bash
mysql -u root -p -e "CREATE DATABASE AcuGrade_AI CHARACTER SET utf8mb4"
mysql -u root -p AcuGrade_AI < sql/schema.sql
python seed_db.py     # subscription plans, badges, the 8 runbooks, a SUPER_ADMIN + sample teacher
```
The seeded admin login is `admin@acugrade.ai` / `ChangeMe123!` —
**change this password immediately** in any non-throwaway environment.

### Run
```bash
python app.py                                    # dev, http://localhost:8000
gunicorn -w 4 -b 0.0.0.0:8000 app:app             # production
```

### Test
```bash
pytest tests/ -v
```
Tests run against an isolated SQLite file (not your configured MySQL) and
force Mistral/ArangoDB off, so they're hermetic and free to run anywhere.

### Cleanup (dev only — refuses to run when `APP_ENV=production`)
```bash
python cleanup_db.py --all
```

## Docs
- `docs/ARCHITECTURE.md` — request flow, RAG, AI fallback strategy, gamification
- `docs/API_DOCUMENTATION.md` — every endpoint, auth requirement, and notes
- `docs/DATABASE.md` — schema conventions + Mermaid ER diagram
- `docs/FRONTEND_BACKEND_MAPPING.md` — how each frontend component maps to these APIs
- `docs/FRONTEND_CHANGES_REQUIRED.md` — exactly what changed in the React app and why

## Known limitations
- Rate limiting is in-process (per-instance) — fine for a single deployment,
  swap for a Redis-backed limiter before scaling horizontally.
- Subscription upgrades don't go through a payment processor — see
  `docs/FRONTEND_BACKEND_MAPPING.md` §2.7. Treat `/subscriptions/upgrade`
  as an admin/self-service tier change until billing is integrated.
- ArangoDB and the ChromaDB-backed document RAG pipeline are both fully
  wired but optional — the app runs correctly with neither configured,
  falling back to structured runbook-only retrieval (see
  `docs/ARCHITECTURE.md`).
- `datetime.utcnow()` is used throughout (not the newer timezone-aware
  `datetime.now(UTC)`); it still works correctly on current Python but
  emits deprecation warnings — a mechanical find/replace across
  `controller/`, `helper/`, and `model/` before it's actually removed
  upstream.

## Recommended next steps
- Add Alembic migrations on top of `sql/schema.sql` for future schema changes.
- Add a `docker-compose.yml` (MySQL + backend + frontend) for one-command local spin-up.
- Swap the in-process rate limiter for Redis if deploying more than one instance.
- Wire a real payment processor behind `/subscriptions/upgrade`.
- Normalize `board`/`classGrade`/`subject`/`topic` into real curriculum
  tables (see `docs/DATABASE.md`) if cross-topic prerequisite graphs become
  a priority — the ArangoDB layer is already there to receive them.
