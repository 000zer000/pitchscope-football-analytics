# PitchScope

This is an isolated repository. Do not modify neighbouring projects or application materials.
Do not push, publish, spend money or create external resources without explicit permission.
Public GitHub publication and zero-cost compatible hosting are explicitly authorized by the user. Never deploy raw provider-data responses without resolving redistribution rights. All UI, reports, errors and project documentation must be in English.
Preserve real player names and original provider attributes without translating identities.

Read README.md, docs/progress.md and docs/methodology.md before continuing.
Python 3.12+, native PostgreSQL 17 for production/CI, SQLAlchemy 2.0, React/TypeScript/Vite.
Use uv.lock and frontend/package-lock.json. No provider downloads in HTTP request paths.
Ingestion is an administrative CLI, never a public HTTP endpoint.

Keep calculations in backend/app/metrics.py or services.py. API and PDF must consume
the same service. Do not duplicate rate calculations in the browser. Never impute
90 minutes to missing playing time or claim to have trained StatsBomb's xG model.
Do not commit data/raw. backend/tests/fixtures.py is synthetic test data only.
Changes to transformation rules or stored role names require a version bump and
an explicit atomic rebuild. Current transformation 1.3.0 uses explicit provider roles and an Unknown fallback.

Checks: uv run ruff check backend scripts/*.py; uv run ruff format --check backend
scripts/*.py; TEST_DATABASE_URL=<dedicated disposable _test database> uv run pytest;
cd frontend && npm test && npm run build && npm run e2e.

Integration tests recreate and delete business tables in the test database.
Never point them at the demo database. CI uses native PostgreSQL; local PGlite is
an explicitly documented fallback, not proof of Docker/native validation.
PGlite accepts one connection here: stop the API before migration/import/rebuild.
Render and visually inspect final PDFs and responsive UI. Distinguish executed
checks from configured workflows. Make coherent local commits; never commit
.env, raw data, databases, caches, installed dependencies or browser binaries.
