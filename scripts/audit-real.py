"""Offline, independent expected clocks transcribed from three real source files."""

import json
from pathlib import Path

from app.db import engine
from app.models import Appearance, Event, Match
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# Manually inspected raw timestamps, not computed with the transformation under test.
# Seconds: England-Iran = 59:03.591 + 58:05.758.
# Wales-Iran = 49:27.292 + 57:08.883; Hennessey red at P2 38:43.633.
# Final = 52:34.569 + 53:37.921 + 16:04.648 + 19:07.472; shootout excluded.
EXPECTED = {
    3857271: {"seconds": 7029.349, "player": "Alireza Safar Beiranvand", "played_seconds": 1152.154},
    3857273: {"seconds": 6396.175, "player": "Wayne Hennessey", "played_seconds": 5290.925},
    3869685: {"seconds": 8484.610, "player": "Ousmane Dembélé", "played_seconds": 2432.571},
}
results = []
with Session(engine) as db:
    for mid, expected in EXPECTED.items():
        match = db.get(Match, mid)
        assert abs(match.duration * 60 - expected["seconds"]) < 0.001
        event = db.scalar(
            select(Event).where(
                Event.match_id == mid, Event.payload["player"]["name"].astext == expected["player"]
            )
        )
        appearance = db.get(Appearance, (mid, event.player_id))
        assert appearance.minutes is not None
        assert abs(appearance.minutes * 60 - expected["played_seconds"]) < 0.001
        shots = db.scalars(select(Event).where(Event.match_id == mid, Event.kind == "Shot")).all()
        goals = sum(e.payload["shot"]["outcome"]["name"] == "Goal" for e in shots if e.period <= 4)
        assert goals == match.home_score + match.away_score
        results.append(
            {
                "match_id": mid,
                "duration_minutes": match.duration,
                "checked_player": expected["player"],
                "checked_minutes": appearance.minutes,
                "goals_before_shootout": goals,
                "shootout_shots": sum(e.period == 5 for e in shots),
                "substitutions": db.scalar(
                    select(func.count())
                    .select_from(Event)
                    .where(Event.match_id == mid, Event.kind == "Substitution")
                ),
            }
        )
Path("docs/real-match-audit.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
print(json.dumps(results, indent=2, ensure_ascii=False))
