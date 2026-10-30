# PitchScope

A local, verifiable football analytics application: player search, contextual
comparison, match-event inspection and backend-generated PDF scouting reports.
**Real demonstration data: 64/64 matches from the 2022 World Cup, 680 players
with appearances, 32 teams and 234,637 events.** The interface, API messages,
reports and documentation are in English.

[Public repository](https://github.com/000zer000/pitchscope-football-analytics) ·
[CI checks](https://github.com/000zer000/pitchscope-football-analytics/actions/workflows/ci.yml)

Compare players in an explicit tournament/role/minutes reference group, inspect
the underlying match events, and export the same statistics as a PDF. The project
demonstrates Python, SQL, API design, TypeScript frontend work and reproducible data
engineering. Provider xG is supplied by StatsBomb, not trained by this project.

No live application URL is claimed: [hosting and data-rights gates](docs/public-demo-readiness.md).
Native PostgreSQL, Chromium E2E and clean Compose validation passed in
[GitHub Actions](https://github.com/000zer000/pitchscope-football-analytics/actions/runs/41114023347).
See [validation progress](docs/progress.md) for exact scope and results. [Recruiter material and learning exercise](docs/recruiter-summary.md).

## Start locally

Prerequisites: Python 3.12+, uv, Node 24 and npm. Run from this repository:

```bash
make setup
make download       # separate, pinned provider download with SHA-256 verification
make local          # database, migrations, cached import, API and frontend
```

Open http://127.0.0.1:5173 ; API documentation: http://127.0.0.1:8000/docs.
The prepared local checkout already has the ignored raw cache and database.
Press Ctrl+C to stop. Ports: 5173, 8000, 55432. Stop the API before administrative
operations under PGlite, which accepts one connection in this setup.

Existing transformation versions require an explicit rebuild before importing
again. Version 1.2.0 stores English role groups. Start the local database alone
if a rebuild is required:

```bash
npm ci --prefix scripts/local-db
PGLITE_DATA="$PWD/work/pglite" node scripts/local-db/server.mjs
# In another terminal, with the API stopped:
PYTHONPATH=backend uv run python -m app.ingest rebuild
```

## Docker Compose

The clean Compose validation job passed on GitHub Linux; see progress.md for the exact run.

```bash
cp .env.example .env
docker compose up --build -d
LOCAL_UID=$(id -u) LOCAL_GID=$(id -g) docker compose --profile admin run --rm ingest download
LOCAL_UID=$(id -u) LOCAL_GID=$(id -g) docker compose --profile admin run --rm ingest import
```

Open http://localhost:8080. Migrations run on API startup. PostgreSQL is internal;
only the web binds to loopback. The database volume persists across `compose down`.
Raw JSON is mounted only into the administrative CLI, not the web application.
Use a separate disposable Compose project for clean-install verification; never
remove an existing data volume merely to run a test.

## Architecture

```text
frontend/src/          React, TypeScript, Vite, Tailwind, TanStack Query, Recharts
backend/app/main.py    FastAPI routes, validation, bounded parameters
           services.py SQL aggregation and comparison shared by API and PDF
           metrics.py  Pure appearance/minutes and per-match transformations
           ingest.py   Administrative download/import/rebuild CLI
           models.py   SQLAlchemy 2 relational schema, JSONB, constraints and indexes
           report.py   ReportLab PDF; local assets only
backend/alembic/        Versioned schema migrations
backend/tests/         Original synthetic fixtures and PostgreSQL integration tests
frontend/e2e/          Playwright user journey with screen/API/PDF checks
```

A simple monolith without accounts, authentication, Redis or distributed services.
Frequently queried fields are structured; variable event attributes remain JSONB.
Appearance counters are derived data and are rebuilt atomically. No business
calculations are duplicated in the browser.

For this small dataset, SQL aggregates players before Python search/sorting and
pagination. This deliberately simple compromise would need SQL-side filtering
and EXPLAIN ANALYZE before scaling to many seasons. Sort keys are allowlisted.
TanStack Query caches for 60 seconds and deduplicates requests; search is debounced
250 ms. Event responses are limited to 500 per page.

## Source, reproducibility and rights

Official source: https://github.com/hudl/open-data.
Pinned commit: `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`.
`data/source-lock.json` records all match IDs and hashes for 130 JSON files.
Changing source versions requires an explicit new manifest and separate database;
download refuses a divergent manifest. Normal browsing never downloads provider data.

```bash
# DATABASE_URL must point to a migrated database; stop the API under PGlite.
PYTHONPATH=backend uv run python -m app.ingest import --limit 3
PYTHONPATH=backend uv run python -m app.ingest import   # repeat: unchanged
PYTHONPATH=backend uv run python -m app.ingest rebuild # atomic, offline
```

Hashes and Pydantic structure validation precede import. Each match uses a
transaction, unique constraints and an advisory lock. Failures roll back, appear
in the import summary and cause a failing exit status. Resuming imports only
missing matches. Different provenance or transformations are never silently
substituted. Rebuild uses stored events/lineups; an older 001 database loads
its missing lineup metadata once from the hash-verified local cache.

[Statistical conventions](docs/methodology.md) and [separate data rights](docs/data-rights.md).
xG is supplied by StatsBomb. Elapsed minutes include stoppage/extra time, exclude
breaks and subtract temporary absences. In-match penalties count; shootouts do
not. Own goals are not credited to a shooter. Missing values are N/A, with
reasons. Initial role is defined per appearance. No talent score or generated
tactical narrative is produced.

Original code is MIT licensed; StatsBomb data and logo are not. Raw data is
excluded from Git and the source archive. No public API or deployment was created.
Review provider terms before any public or commercial distribution.

## Checks

```bash
uv run ruff check backend scripts/*.py
uv run ruff format --check backend scripts/*.py
# Disposable test database only: business tables are recreated and deleted.
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/pitchscope_test uv run pytest -q --require-postgres
cd frontend
npm ci
npm test
npm run build
npx playwright install chromium
npm run e2e  # API and frontend must be running
```

The required --require-postgres mode fails for an unavailable/non-native database
or any skipped test. Without that flag, local unit-only runs may explicitly skip
integration tests when TEST_DATABASE_URL is absent. Never use the demo
database for tests or run scripts/seed-test.py against it. CI uses native
PostgreSQL and original synthetic fixtures, with no provider requests. A
configured workflow is not a successful GitHub Actions run.

```bash
PYTHONPATH=backend uv run python scripts/audit-real.py
uv run python scripts/benchmark.py
```

[Real match audit](docs/real-match-audit.json): replacement, red card, extra time
and shootout cases. [Benchmark](docs/benchmark.json): machine, dataset, two warmups,
ten sequential localhost requests per endpoint and measured medians. These are
not production scalability or concurrency claims.

## Demonstration and interview

[90-second script](docs/demo-90-seconds.md) · [Interview guide](docs/interview-guide.md) ·
[Progress and remaining checks](docs/progress.md).

Comparison: `/?view=compare&left=5503&right=3009&role=Forward&min=180`.
Final: `/?view=matches&match=3869685`. Filters and comparisons are shareable by URL.

![Real player explorer](docs/screenshots/explorer-desktop.jpg)

[Comparison](docs/screenshots/comparison-desktop.jpg) ·
[Match and source](docs/screenshots/match-desktop.jpg) ·
[Mobile](docs/screenshots/explorer-mobile.jpg)

## Configuration and security

See .env.example. Compose reads .env; local Python reads exported shell variables,
without implicit dotenv loading. CORS is restricted to expected origins. SQLAlchemy
binds parameters; sorting and pagination are allowlisted/bounded. Readiness
executes SELECT 1. PDF generation reads only database values and a local logo,
never a client-supplied URL. There is no public ingestion route. This unauthenticated
V1 is for local use and must not be exposed to the Internet as-is.
