# Interview preparation

This guide describes the delivered code and observed validation. It does not
invent past experience for the student. Rehearse the demo and trace a metric
before presenting the project.

## A 30-second introduction

“PitchScope is a local player research and comparison tool. It turns pinned
StatsBomb events into verifiable statistics. A Python/PostgreSQL backend computes
the same values for the browser and PDF, and a match view links observations to
source events. The demonstration covers the complete 2022 World Cup.”

## Architecture

React/TypeScript and TanStack Query call FastAPI. Routes validate parameters and
delegate to SQL-backed services. SQLAlchemy 2 queries PostgreSQL appearances and
events. `metrics.py` reconstructs playing time and per-match counters. The local
import CLI records hashes, source commit and transformation version. Alembic
manages schema changes. ReportLab renders the same `comparison()` result. Nginx
serves Vite's production build and proxies /api in Compose.

## Three concrete tradeoffs

1. **One complete tournament.** Coverage is verifiable and the demo is focused,
   but opponents and sample sizes differ; seven games cannot establish potential.
2. **Derived appearances plus event JSONB.** Structured counters simplify frequent
   queries; JSONB preserves variable attributes and traceability. This costs
   storage and requires atomic reconstruction when rules change.
3. **Initial role per appearance.** The first lineup position defines a stable
   context. Later tactical switches are not modelled as intervals, so the figures
   do not describe each tactical phase separately.

## Difficulties actually encountered

- Period clocks restart. The final contains 141.4102 elapsed minutes excluding
  breaks in these files, versus 120 nominal minutes. The `minute` field alone
  loses stoppage-time information.
- SQL match joins were ambiguous because a team can be home or away. The join
  was made explicit with `Match.id == Appearance.match_id`.
- Native PostgreSQL cannot initialise in this sandbox because shared-memory
  syscalls are denied. PGlite enabled local SQL tests, but it does not prove
  native multi-process or concurrent behaviour.
- Chromium's Playwright runner is blocked by macOS Mach-port restrictions before
  the test starts. The integrated browser provided initial inspection; native
  PostgreSQL and Chromium were subsequently verified in green Linux CI runs.
- psycopg prepared statements conflicted across PGlite's shared connection.
  Prepared statements were disabled, its local pool limited to one connection,
  and administrative work performed with the API stopped.
- English role names are stored in appearances. Switching the product to English
  therefore required an explicit versioned rebuild, not just relabelling the UI.

## Trace an xG value from JSON to PDF

1. `events/<match_id>.json` contains a Shot ID in period 1–4 and supplied
   `shot.statsbomb_xg`. StatsBomb provides this value; PitchScope trains no model.
2. `cached()` checks SHA-256 before parsing. Pydantic validates event structure,
   references and shot attributes, including the xG range.
3. `reconstruct()` sums xG per appearance, excludes shootouts and makes a total
   unavailable if a source xG is absent.
4. A transaction stores the original event JSONB and derived appearance counters,
   minutes and role. ImportRecord links hashes, commit and transformation version.
5. `services.stats()` aggregates filtered appearances. xG/90 uses only reliable
   appearances. `comparison()` adds an explicit reference group.
6. `/api/compare` serialises the result, React displays it without business
   recalculation, and `/api/report.pdf` passes the same result to ReportLab.
   Tests extract PDF text and compare values rounded to two decimal places.
7. The shot map exposes the original event ID and attributes and links to the
   source file at the pinned commit.

## Questions to prepare

- Why use sum(completed)/sum(attempted), rather than averaging percentages?
- How is ingestion idempotence proven? What if insertion fails halfway through?
- Why combine an advisory lock with unique constraints?
- How do measured zero and missing data differ?
- How do periods distinguish in-match penalties from a shootout?
- When should a frequently queried JSONB attribute become an indexed column?
- How would another season be added without mixing reference groups?
- Why do localhost timings not establish production scalability or concurrency?
- How does atomic reconstruction prevent mixed transformation versions?
- Which checks actually ran in GitHub Actions? At delivery: none; workflow only.

## Later work, only after V1 validation

Similar-player search, interval-based roles, multiple seasons and context-adjusted
metrics. Tracking, 360 data, ML and LLM features are not implemented in this V1.
