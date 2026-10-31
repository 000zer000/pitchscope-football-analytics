"""Independent, hand-counted midrank examples; no provider data required."""

from types import SimpleNamespace

import pytest
from app import services


def test_midrank_ties_missing_zero_and_threshold(monkeypatch):
    # 20 eligible observations: [0, 0, 2, 3, ..., 19]. Two zeros share 5th percentile.
    rows = [
        dict(id=i, minutes=500, shots_p90=0 if i < 2 else i, xg_p90=None if i == 19 else i, passes_p90=i)
        for i in range(20)
    ]
    rows.append(dict(id=20, minutes=10, shots_p90=100, xg_p90=100, passes_p90=100))
    monkeypatch.setattr(services, "stats", lambda *a: [dict(p) for p in rows])
    db = SimpleNamespace(get=lambda *a: SimpleNamespace(source_commit="synthetic-test-only"))
    result = services.comparison(db, 0, 19, "Forward", 180)
    assert result["population"]["count"] == 20
    assert result["players"][0]["percentiles"]["shots_p90"] == 5
    assert result["players"][1]["percentiles"]["shots_p90"] == 97.5
    # Only 19 non-missing xG rates: suppress this metric, even with 20 players.
    assert "xg_p90" not in result["players"][0]["percentiles"]
    result = services.comparison(db, 20, 0, "Forward", 180)
    assert result["players"][0]["percentiles"] == {}
    assert "below" in result["warnings"][0]
    result = services.comparison(db, 0, 1, "Forward", 600)
    assert result["population"]["count"] == 0
    assert all(p["percentiles"] == {} for p in result["players"])
    with pytest.raises(ValueError):
        services.comparison(db, 999, 0, "Forward", 180)
