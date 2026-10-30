# PitchScope v1.0.0

A verifiable football analytics portfolio project with a FastAPI/PostgreSQL
backend, React/TypeScript frontend, match-event inspection and shared API/PDF
calculations. English interface, documentation and reports.

- Complete pinned 2022 World Cup scope: 64 matches, 32 teams, 680 players with
  appearances and 234,637 events. Raw dataset is not distributed in the repository.
- Explicit role/minutes reference populations, source IDs and import hashes.
- Reconstructed elapsed playing time; penalties, own goals, extra time and
  shootouts handled by documented conventions. xG is supplied by StatsBomb.
- 17 backend tests on native PostgreSQL, 2 frontend tests, Chromium browser journey,
  Ruff/TypeScript/build checks and clean Compose/persistence validation.
- Real-data automated journey, comparison PDF, screenshots, 90-second demo script,
  interview guide and guided code exercise.

Validation baseline:
https://github.com/000zer000/pitchscope-football-analytics/actions/runs/41114020862
Real-data validation:
https://github.com/000zer000/pitchscope-football-analytics/actions/runs/41114023347
The release target is checked again before tagging.

Limitations: descriptive tournament sample; no trained xG model, tracking,
recruitment recommendations or production scalability claims. No live deployment:
compatible hosting authentication and the raw-event redistribution contract remain
unresolved. See docs/public-demo-readiness.md. No payment, card or subscription.

Original code: MIT. StatsBomb data/logo: separate provider rights and attribution.
The attached video is an actual automated browser recording, not a deployed app.
