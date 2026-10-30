# Reproducible 90-second demonstration

Prerequisite: real data downloaded/imported and the app open at
http://127.0.0.1:5173 (or http://localhost:8080 with Compose).
Never demonstrate synthetic CI fixtures as real football data.

- **0–15 s:** show 64/64 matches, 680 players and pinned provenance. Explain
  that the scope is one complete tournament rather than a club season.
- **15–30 s:** search “Messi”, choose Forward and a 180-minute threshold,
  select him, then search “Mbappé” and select him.
- **30–50 s:** Compare players. Show reference-group size, minutes, goals,
  provider xG and per-90 bars. Explain stoppage-time inclusion and the absence
  of a talent score.
- **50–70 s:** open a profile, then Argentina–France on 18 December 2022.
  Select a shot to inspect its source ID, xG and available attributes. Show
  shootout attempts separately from match shots.
- **70–85 s:** return to Comparison, export the PDF and verify an xG value
  against the screen.
- **85–90 s:** open Methodology and show source, commit, hashes and limitations.

Direct comparison:
`/?view=compare&left=5503&right=3009&role=Forward&min=180`

Final: `/?view=matches&match=3869685`.
The equivalent runner scenario is `frontend/e2e/journey.spec.ts`. It selects the
two forwards with most minutes so it can also run on clearly synthetic CI data.
