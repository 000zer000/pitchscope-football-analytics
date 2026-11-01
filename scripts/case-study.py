"""Export a small attributed analysis, using the application's SQL services (read only)."""

import argparse
import base64
import json
from pathlib import Path
from xml.sax.saxutils import escape

from app.db import engine
from app.services import comparison, coverage
from sqlalchemy.orm import Session

IDS = [5503, 3009, 29560]  # Messi, Mbappé, Álvarez; selected before inspecting metric ordering.
KEYS = ["minutes", "shots", "goals", "xg", "penalties", "shots_p90", "xg_p90", "passes_p90", "pass_pct"]
LABELS = [
    ("shots_p90", "Shots / 90 min"),
    ("xg_p90", "StatsBomb xG / 90 min"),
    ("passes_p90", "Passes / 90 min"),
]


def canonical(value):
    """Stable analysis export; SQL floating SUM order can differ below 1e-9."""
    if isinstance(value, float):
        return round(value, 9)
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return [canonical(v) for v in value]
    return value


def build(db):
    c = coverage(db)
    if c["imported_matches"] != 64 or c.get("synthetic"):
        raise ValueError("Case study requires the complete real tournament, never synthetic fixtures")
    pairs = [comparison(db, IDS[0], other, "Forward", 180) for other in IDS[1:]]
    players = [pairs[0]["players"][0], pairs[0]["players"][1], pairs[1]["players"][1]]
    assert all(p["minutes"] >= 450 for p in players)
    return canonical(
        {
            "source": "StatsBomb Open Data / hudl/open-data",
            "source_commit": pairs[0]["source_commit"],
            "transform_versions": sorted({i["transform_version"] for i in c["imports"]}),
            "population": pairs[0]["population"],
            "players": [
                {k: p[k] for k in ["id", "name", "teams", "appearances", *KEYS, "percentiles"]}
                for p in players
            ],
        }
    )


def chart(data):
    # Standalone vector chart: publication contains aggregates, never event payloads.
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650" role="img" aria-labelledby="title desc">',
        '<title id="title">Three forwards, three volume profiles</title>',
        '<desc id="desc">Grouped horizontal bars with zero baselines. Exact per-90 values appear beside every bar; scales differ by metric.</desc>',
        '<rect width="1000" height="650" fill="#f5f8f3"/>',
        '<g font-family="DejaVu Sans,Arial,sans-serif" fill="#243e32">',
        '<text x="30" y="38" font-size="24" font-weight="bold">Three forwards, three volume profiles</text>',
        '<text x="30" y="65" font-size="13">World Cup 2022 · Forward appearances · ≥180 reliable minutes · 69 reference players</text>',
    ]
    colours = ["#2c7259", "#668bc0", "#aa7841"]
    for j, (key, label) in enumerate(LABELS):
        y = 104 + j * 145
        out.append(f'<text x="30" y="{y}" font-size="15" font-weight="bold">{label}</text>')
        maximum = max(p[key] for p in data["players"]) * 1.1
        for i, p in enumerate(data["players"]):
            yy = y + 13 + i * 31
            width = 470 * p[key] / maximum
            out += [
                f'<text x="30" y="{yy + 15}" font-size="12">{escape(p["name"])}</text>',
                f'<rect x="360" y="{yy}" width="{width:.3f}" height="21" rx="3" fill="{colours[i]}"/>',
                f'<text x="{370 + width:.3f}" y="{yy + 15}" font-size="12">{p[key]:.2f}</text>',
            ]
        out.append(
            f'<text x="360" y="{y + 124}" font-size="10">0 · common scale within this metric; scales differ between metrics</text>'
        )
    out += [
        '<text x="30" y="565" font-size="13">Descriptive volume only. In-match penalties included; shootouts excluded.</text>',
        '<text x="30" y="587" font-size="12">Source: StatsBomb Open Data. xG supplied by StatsBomb; no model trained.</text>',
        '<text x="30" y="610" font-size="11">Short tournament; initial role per appearance; no opponent or possession adjustment.</text>',
        '</g><image href="data:image/png;base64,'
        + base64.b64encode(Path("assets/statsbomb.png").read_bytes()).decode()
        + '" x="830" y="555" width="145" height="60"/></svg>',
    ]
    return "\n".join(out)


def article(data):
    players = data["players"]
    rows = []
    for p in players:
        rows.append(
            f"| {p['name']} | {p['appearances']} | {p['minutes']:.2f} | {p['shots']} | "
            f"{p['goals']} | {p['xg']:.2f} | {p['penalties']} | {p['shots_p90']:.2f} | "
            f"{p['xg_p90']:.2f} | {p['passes_p90']:.2f} |"
        )
    return (
        """# Three forwards, three volume profiles

How did Messi, Mbappé and Álvarez differ in shot volume, provider xG and passing
involvement during the 2022 World Cup? This is a descriptive starting point for
choosing match footage to review, rather than a recommendation to recruit anyone.

## Selection and reference group

The subjects are three recognisable finalists with at least 450 reliable minutes
in Forward appearances: Messi and Álvarez from Argentina, Mbappé from France.
This is a purposive example, not a search for the tournament's best players.
The reference group is all 69 players with at least 180 reliable minutes in
Forward appearances across the complete 64-match tournament. No team filter.
The subject inclusion rule (450 minutes) and reference threshold (180) differ
intentionally; neither removes short-tournament uncertainty. Only appearances
whose initial provider lineup position maps to Forward contribute here.

![Three volume comparisons with labelled values](case-study.svg)

Scales start at zero and are shared within each metric; they differ between metrics.

| Player | Role appearances | Reliable min | Shots | Goals | StatsBomb xG | Penalty shots | Shots/90 | xG/90 | Passes/90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
"""
        + "\n".join(rows)
        + """

## Observations and practical interpretation

Mbappé recorded 4.04 shots per 90 reliable minutes, Messi 3.64 and Álvarez 1.91.
Messi's provider xG per 90 was 0.69, ahead of Mbappé's 0.55 and Álvarez's 0.35
in this sample. These orderings differ: more shots alone do not establish better
chances or a better player. In-match penalty shots (5, 2 and 0 respectively) are
included, so the xG comparison must not be presented as an open-play comparison.

Messi attempted 42.21 passes per 90, Mbappé 30.37 and Álvarez 22.15. This describes
recorded passing involvement in these role appearances; it does not measure
creativity, progressive passing or pass difficulty. Those metrics are not available.
Álvarez has six Forward appearances here, rather than seven assumed full matches.
Minutes are elapsed playing time, not nominal match durations.

Against the reference population, Messi's displayed volume percentiles are P89
for shots/90, P98 for xG/90 and P91 for passes/90; Mbappé's are P96, P91 and P63;
Álvarez's are P47, P73 and P41. These are rounded empirical midranks with ties,
not quality ratings or probabilities. Aggregates and percentiles exported to nine decimal places
are in [the reproducible export](case-study.json).

The useful next step is to review how those actions arose: for example, inspect
the final in Match centre, distinguish an in-match penalty from a shootout,
and select a shot to see its source ID and provider xG. The figures can guide
questions for video review; they cannot answer tactical or recruitment questions
on their own. Goals (7, 8 and 4) remain descriptive outcomes, not evidence of a
stable finishing ability or future performance.

## Limits and uncertainty

A short tournament has few matches and an uneven distribution of minutes.
Teammates, opponents, score state, set pieces, penalties, substitution patterns
and team possession affect opportunities. Role groups are coarse and fixed by
the initial lineup position for each appearance; they do not capture tactical
changes. Argentina and France do not have identical schedules or contexts.
Per-90 scaling does not remove these differences. Small samples can change the
ordering sharply; no confidence interval, causal effect or career prediction is
claimed. xG is supplied by StatsBomb; PitchScope did not train the provider model.

## Reproduce and compare with the application

Use the existing migrated, fully imported database. This command reads only;
never point test schema recreation at the demonstration database. With PGlite,
stop the API while leaving the database running because only one connection is
supported in this setup. Export DATABASE_URL for the chosen database/port first.

```bash
PYTHONPATH=backend uv run python scripts/case-study.py --output work/case-study --check docs/case-study.json
```

This calls `services.comparison` and `services.coverage`, the same SQL-backed
services as the API and PDF. It refuses incomplete or synthetic tournaments,
asserts the subject minutes, and checks stored JSON equality after rounding
exports to nine decimal places. This avoids insignificant differences from SQL
floating-point SUM order across PostgreSQL builds; application rates are unchanged. It exports
this article, a vector chart and a small aggregate JSON analysis. No provider
event payloads or raw files are exported. CI repeats the command on native
PostgreSQL after the pinned import and compares screen values with this JSON.
The screenshot and PDF checks compare all shared metric values with the API.

Open locally:
- Messi/Mbappé: `/?view=compare&left=5503&right=3009&role=Forward&min=180`
- Messi/Álvarez: `/?view=compare&left=5503&right=29560&role=Forward&min=180`
- Final: `/?view=matches&match=3869685`

Conventions for minutes, temporary absences, red cards, missing values, weighted
ratios and shootout exclusion are unchanged: [methodology](methodology.md).
Source: StatsBomb Open Data / hudl/open-data, pinned commit
`4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, transformations `TRANSFORM_VERSION_LABEL`.
This attributed non-commercial research example shares analysis, not a dataset;
[provider rights](data-rights.md) still apply. No raw-event public API is deployed.

![StatsBomb](../assets/statsbomb.png)
"""
    ).replace("TRANSFORM_VERSION_LABEL", ", ".join(data["transform_versions"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("work/case-study"))
    parser.add_argument(
        "--check", type=Path, help="Assert exact agreement with a previously exported JSON analysis"
    )
    args = parser.parse_args()
    with Session(engine) as db:
        data = build(db)
    if args.check:
        assert json.loads(args.check.read_text()) == data, "Case study differs from application services"
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "case-study.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (args.output / "case-study.svg").write_text(chart(data))
    (args.output / "case-study.md").write_text(article(data))
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
