# PitchScope v1.1.0

This release repairs the comparison presentation and supplies a reproducible
three-forward study, refreshed real screenshots, a captioned real demonstration
and sample reports. The existing football conventions and transformation 1.2.0
are preserved. No new metric or predictive model was introduced.

- Numeric backend percentiles replace the malformed template. Human metric
  labels and full player names identify the comparison.
- Bar animation is disabled after reproducing empty early captures with valid
  data and later non-zero SVG geometry. Browser regressions now inspect coloured
  bars, relative lengths, visible numbers and API percentile text.
- Nulls, zero, long accented names, insufficient populations and threshold
  warnings have targeted coverage. Responsive journeys run at 390 and 1440 px.
- The case study uses application SQL services and a pinned complete tournament.
  Exports use nine decimal places to avoid insignificant floating SUM-order
  differences across builds. Screen and PDF still show the same two decimals.
- Reports with long and extended Latin names were rendered and visually checked.
  Raw-event payloads/datasets are excluded from the public release.
- Local startup checks port availability before opening the persistent database.
  Demo coverage and all import records remained unchanged during verification.

Validation baseline: 18 backend tests on isolated native PostgreSQL 17.10, four
Vitest checks, Ruff, TypeScript/build, Chromium comparison and responsive journeys.
Clean Compose migrations, repeated import, PDF and restart persistence run in CI.
The real-data workflow also imports all 64 matches twice, audits source clocks,
checks the case study, executes five Chromium scenarios and packages the roughly
92-second captioned MP4. Release notes on GitHub identify the final exact commit
and successful required/real-data run links, rather than claiming a configured
workflow alone as evidence.

Presentation assets are descriptive non-commercial research with StatsBomb
attribution/logo. xG remains provider-supplied. Original code is MIT licensed;
provider data and branding are separate. See docs/data-rights.md.

No live application is deployed: compatible hosting requires sign-in, and the
local original-event API needs a resolved redistribution contract before public
exposure. The video and screenshots are recordings of the real running app,
not an application hosting URL. No payment, subscription or domain was created.

Known limits: one short tournament, coarse initial roles, unequal contexts and
penalty exposure, no opponent/possession adjustment or recruitment prediction.
The build still reports a large Recharts bundle; no load-capacity claim is made.
