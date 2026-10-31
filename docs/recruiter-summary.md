# PitchScope — recruiter material

## GitHub description
Verifiable football analytics: FastAPI/PostgreSQL, React/TypeScript, pinned StatsBomb events and reproducible PDF comparisons.

Suggested topics: football-analytics, sports-analytics, python, fastapi, postgresql,
react, typescript, data-engineering, scouting, statsbomb, playwright.

## CV bullet options

- Built an end-to-end football analytics application with FastAPI, PostgreSQL and React/TypeScript, analysing 64 World Cup matches and 234,637 source events with traceable player comparisons and PDF reports.
- Designed a reproducible, hash-verified event ingestion pipeline with transactional imports, idempotence checks and explicit playing-time reconstruction; validated API/PDF consistency and documented provider-data limitations.

Native PostgreSQL integration, Chromium E2E and clean Compose validation have passed in GitHub Actions. This does not establish production load capacity.
xG values are supplied by StatsBomb; no predictive model was trained. No real-user
adoption or unmeasured scalability is claimed.

## LinkedIn draft — not published

PitchScope is my football analytics portfolio project: a Python/FastAPI and
PostgreSQL backend, React/TypeScript interface, contextual player comparisons,
match-event inspection and consistent PDF exports. The demonstration covers the
2022 World Cup with pinned StatsBomb Open Data. I focused on reproducibility,
playing-time conventions and tracing each observation back to source events.
A reproducible case study compares three forwards without turning volume into
a talent score. Source, captioned demo and sample report:
https://github.com/000zer000/pitchscope-football-analytics

## Guided code exercise: add pass volume to the comparison chart

Goal: understand a small existing feature without inventing a new metric.

1. Run the application and locate `passes_p90` in backend/app/services.py.
2. Explain its numerator, denominator and treatment of uncertain appearances.
3. Find the chart metric list in frontend/src/ComparisonCharts.tsx. The existing comparison
   table already contains passes/90; verify whether the chart does too before
   editing. If present, add goals/90 instead, reusing the API's `goals_p90`.
4. Add the chart label and units; never calculate the rate in JavaScript.
5. Run npm test and npm run build, then compare displayed values to /api/compare.
6. Verify keyboard access and the mobile layout. Explain why the chart shares
   the API calculation but uses a separate visual scale.
7. Commit only the small change and describe its validation in two sentences.

Review question: why would averaging match-level rates give a different answer?
See docs/interview-guide.md for the full architecture and JSON-to-PDF walkthrough.
