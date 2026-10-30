# Delivery status — 30 October 2026

## Public verification update

Public repository: https://github.com/000zer000/pitchscope-football-analytics

Required checks passed on native PostgreSQL and Chromium, including clean Docker
Compose startup, migrations, repeated import, PDF export and restart persistence:
https://github.com/000zer000/pitchscope-football-analytics/actions/runs/41114020862

The real-data run also passed, importing the pinned full tournament and executing
the automated browser journey with an actual recording and saved comparison PDF:
https://github.com/000zer000/pitchscope-football-analytics/actions/runs/41114023347

Both runs verified commit 2d6b7fe451f05b420052c763755b23ed42b5672d.
17 backend tests passed on native PostgreSQL, with no skipped integration tests;
2 frontend tests and 1 Chromium E2E passed. Ruff, TypeScript and build passed.
The required --require-postgres mode fails when the database is missing, is
not native PostgreSQL, or any test is skipped. Its missing-database failure
was checked explicitly. Synthetic CI fixtures are clearly labelled in the UI.

No live application is claimed. Hosting login and provider-redistribution gates
are documented in docs/public-demo-readiness.md. No paid resources were created.

The initial service-health quoting defect was fixed. A subsequent uv cache-prune
failure was traced to the background uv-run API holding its cache lock. Setup was
simplified and API process lifecycle made explicit. Earlier failed/cancelled runs
remain visible; no failure was relabelled as a successful check.

The local pre-publication branch is preserved. Public main uses a separate clean
history and GitHub noreply authorship; no force-push or other repository edits.
See docs/publication-audit.md.

## Earlier local validation baseline

The product, PDF, API messages and documentation were converted to English at
the user's request. Transformation 1.2.0 stores English role names; an explicit
atomic rebuild updates the existing database. Player identities and provider
attributes retain their original spelling. Numeric conventions are unchanged.

## Completed milestones

1. Inspected the empty workspace and searched ancestor instructions. Created an
   isolated repository without modifying other projects or application materials.
2. Inspected official JSON, README, five-page licence and event specification.
   Selected the complete 2022 World Cup, pinned the source commit and recorded
   130 JSON hashes. Raw data remains ignored.
3. Demonstrated a vertical slice on three real matches: ingestion, Messi search,
   Messi/Mbappé comparison and a real one-page backend PDF.
4. Imported all 64 matches: 32 teams, 680 players with appearances and 234,637
   events. No synthetic fixtures are present in the demonstration database.
5. Executed atomic reconstruction and complete idempotent reimport (64 unchanged).
6. Bootstrapped a separate empty PGlite database with migrations 001+002, imported
   the full dataset and asserted match/event counts and comparison goals (7/8).
7. Executed ./scripts/dev.sh after stopping old processes: migrations, cached
   idempotent import and readiness through the Vite proxy. No provider download.

## Executed checks

- Backend: 16 Pytest tests, including PostgreSQL SQL integration via psycopg
  against PGlite PostgreSQL 18.6 / 0.5.13 on a separate disposable port 55433.
  No SQLite. The final English rerun passed all 16 tests (work/pytest-en.log).
- Coverage: substitutions, halftime changes, red/second-yellow cards, temporary
  exits, missing returns, extra time, shootouts, own goals, missing xG and lineup roles.
- Pipeline: idempotence, invalid structure/hash rejection, foreign-key rollback,
  recovery after failure and refusal of conflicting provenance.
- Aggregates: weighted pass ratio 2/3, unreliable numerator exclusion, N/A for
  zero denominators, filters, bounded pagination/sorting and API/database consistency.
- PDF: values extracted against the API, one/two-page bound, extended Latin
  names (Pašalić), rendering and visual inspection.
- Ruff check and format --check; TypeScript and Vite build; two Vitest checks
  for unavailable-versus-zero presentation and rounding. A large-bundle warning
  remains because Recharts is included; no mobile-speed or scalability claim.
- uv sync --frozen succeeded. npm audit reported zero vulnerabilities at the
  recorded check; this is not a permanent guarantee.
- Independent source-clock audit: England–Iran (goalkeeper substitution),
  Wales–Iran (Hennessey dismissal), final (extra time and eight shootout attempts).
  See docs/real-match-audit.json.
- Benchmark: two warmups, ten sequential HTTP attempts per endpoint, ARM64 / eight
  logical CPUs, warm PGlite database. Exact measurements in docs/benchmark.json.

## Browser verification

The integrated browser was operated through accessible controls and Playwright
locators, separately from the Chromium runner. Verified search, role/minutes
filters, two-player selection, comparison, profiles, opening the final, shot-map
selection, source inspection, team filtering, PDF download, empty/reset states,
Methodology and import inventory. Desktop 1440 px and mobile 390 px were checked:
document width equals viewport width; tables scroll inside their own container.
Real screenshots are in docs/screenshots; English captures replace French ones.

Reference group: 69 forwards at 180 reliable minutes. Messi/Mbappé xG remains
6.03 / 4.23, identical across API, screen and PDF. The final contains 30
non-shootout shot markers; filtering France leaves ten. Inspected source IDs:
545c2c84-018f-4570-a01c-753823feaeac and Messi's penalty
6d527ebc-a948-4cd8-ac82-daced35bb715 (provider xG 0.7835).

HMR createRoot warnings observed during development led to an explicit unmount
cleanup. TestClient still emits an httpx deprecation warning while passing tests.

## Remaining deployment gates

Native PostgreSQL, Docker and Chromium checks that were blocked locally have now
been executed successfully in Linux CI. GitHub Actions is no longer merely configured.

Only live deployment remains unfulfilled: no compatible hosting login is available,
and the current original-event JSON endpoint needs a resolved redistribution contract
before public exposure. No static simulation is substituted for the application.

## Resume

Read AGENTS.md, README.md and docs/methodology.md. Existing prepared checkout:
make local. Another machine: make setup, make download, make local. The source
archive excludes raw JSON, database files and installed dependencies. Native tests
require a dedicated disposable _test database. Do not begin out-of-scope features
until the remaining V1 checks are completed.
