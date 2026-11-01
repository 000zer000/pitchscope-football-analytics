import json
from copy import deepcopy
from io import BytesIO

import pytest
from app import ingest, services
from app.models import Appearance, Event, ImportRecord, Match, Player
from fixtures import fixture, lineups, meta
from pydantic import ValidationError
from pypdf import PdfReader
from sqlalchemy import func, select


def seed(db, mid=10001, events=None):
    return ingest.import_match(
        db, meta(mid), events or fixture(), lineups(), {"synthetic": "sha-test"}, "synthetic-test-only"
    )


def test_idempotence_invalid_recovery(db):
    assert seed(db) == "imported"
    db.commit()
    assert seed(db) == "unchanged"
    assert db.scalar(select(func.count()).select_from(Event)) == 9
    assert db.scalar(select(func.count()).select_from(ImportRecord)) == 1
    broken = deepcopy(fixture())
    broken[0]["index"] = -1
    with pytest.raises(ValidationError):
        seed(db, 10002, broken)
    db.rollback()
    assert db.scalar(select(func.count()).select_from(Match)) == 1
    e = deepcopy(fixture())
    for row in e:
        row["id"] = "other-" + row["id"]
    assert seed(db, 10002, e) == "imported"
    db.commit()
    assert db.scalar(select(func.count()).select_from(Match)) == 2
    with pytest.raises(ValueError, match="Existing import differs"):
        ingest.import_match(db, meta(), fixture(), lineups(), {"synthetic": "changed"}, "synthetic-test-only")


def test_atomic_rollback_after_foreign_key_error(db):
    e = fixture()
    e[3]["team"]["id"] = 999
    with pytest.raises(Exception):
        seed(db, events=e)
        db.commit()
    db.rollback()
    assert db.scalar(select(func.count()).select_from(Match)) == 0
    assert seed(db) == "imported"


def test_cache_tampering(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "CACHE", tmp_path)
    p = tmp_path / "events.json"
    p.write_text("[{}]")
    with pytest.raises(ValueError, match="Hash mismatch"):
        ingest.cached("events.json", "0" * 64)
    p.write_text("invalid")
    with pytest.raises(json.JSONDecodeError):
        ingest.cached("events.json")
    with pytest.raises(ValueError, match="Missing file"):
        ingest.cached("missing.json")


def test_sql_totals_rates_filters_and_pagination(client, db):
    seed(db)
    db.commit()
    rows = {p["id"]: p for p in services.stats(db)}
    assert rows[1]["pass_pct"] == 50
    assert rows[1]["shots_p90"] == pytest.approx(90 / 62)
    assert rows[3]["pass_pct"] is None
    assert rows[2]["xg"] == 0.25
    # Second match: 1 completed pass, so weighted ratio = 2/3, not mean(50,100)=75.
    e = deepcopy(fixture())
    for row in e:
        row["id"] = "two-" + row["id"]
    e = [r for r in e if r["index"] != 3]
    seed(db, 10002, e)
    db.commit()
    assert {p["id"]: p for p in services.stats(db)}[1]["pass_pct"] == pytest.approx(200 / 3)
    r = client.get(
        "/api/players", params={"role": "Forward", "min_minutes": 50, "sort": "minutes", "size": 1}
    )
    assert r.status_code == 200 and r.json()["total"] == 2
    assert r.json()["items"][0]["id"] == 1
    assert client.get("/api/players?page=2&size=1&sort=minutes").json()["items"][0]["id"] == 1
    assert client.get("/api/players?q=alpha&team=100").json()["total"] == 1
    assert client.get("/api/players?team=200").json()["total"] == 0
    assert client.get("/api/players?size=501").status_code == 422
    assert client.get("/api/players?sort=drop%20table").status_code == 422
    assert client.get("/api/players?season=bad").status_code == 422
    assert client.get("/api/players/999").status_code == 404
    assert client.get("/api/matches/10001/events?size=501").status_code == 422
    events = client.get("/api/matches/10001/events?kind=all&size=2").json()
    assert events["total"] == 9 and len(events["items"]) == 2
    assert events["summary"][0]["shots"] == 2
    assert events["summary"][0]["xg"] == 1.0
    assert client.get("/api/matches/10001/events?kind=Shot&player=2").json()["items"][0]["id"] == "test-8"


def test_uncertain_numerator_excluded_and_rebuild(db, monkeypatch):
    seed(db)
    db.commit()
    e = deepcopy(fixture())
    for row in e:
        row["id"] = "two-" + row["id"]
    e = [r for r in e if r["index"] != 9]
    seed(db, 10002, e)
    db.commit()
    p = {p["id"]: p for p in services.stats(db)}[1]
    assert p["shots"] == 2 and p["uncertain_appearances"] == 1
    assert p["shots_p90"] == pytest.approx(90 / 62)
    engine = db.get_bind()
    db.close()
    monkeypatch.setattr(ingest, "engine", engine)
    ingest.rebuild()
    assert db.scalar(select(func.count()).select_from(Appearance)) == 6
    assert {p["id"]: p for p in services.stats(db)}[1]["shots_p90"] == pytest.approx(90 / 62)


def test_unknown_role_visible_overall_but_excluded_from_forward_cohort(client, db):
    events = deepcopy(fixture())
    for e in events:
        if e["type"]["name"] == "Substitution":
            e.pop("position", None)
    ingest.import_match(db, meta(), events, lineups(), {"synthetic": "sha-test"}, "synthetic-test-only")
    db.commit()
    all_rows = {p["id"]: p for p in services.stats(db)}
    assert all_rows[2]["roles"] == ["Unknown"]
    assert all_rows[2]["minutes"] == 33
    assert {p["id"] for p in services.stats(db, role="Forward")} == {1}
    response = client.get("/api/compare?left=1&right=2&role=Forward&min_minutes=0")
    assert response.status_code == 422


def test_pdf_api_contract_and_small_population(client, db):
    seed(db)
    db.commit()
    query = "left=1&right=2&role=Forward&min_minutes=0"
    data = client.get("/api/compare?" + query).json()
    assert data["population"]["count"] == 2
    assert data["players"][0]["percentiles"] == {}
    assert data["warnings"]
    response = client.get("/api/report.pdf?" + query)
    assert response.status_code == 200 and len(response.content) > 5000
    pdf = PdfReader(BytesIO(response.content))
    assert 1 <= len(pdf.pages) <= 2
    text = "\n".join(p.extract_text() for p in pdf.pages)
    assert "TEST Alpha" in text and "TEST Beta" in text
    for p in data["players"]:
        for key in ["minutes", "xg", "shots_p90", "pass_pct"]:
            if p[key] is not None:
                assert f"{p[key]:.2f}" in text
    assert "synthetic-test-only" in text
    assert client.get("/api/compare?left=1&right=1").status_code == 422
    assert client.get("/api/report.pdf?left=1&right=999").status_code == 422
    assert client.get("/api/ready").json() == {"status": "ready"}


def test_pdf_preserves_extended_latin_names(client, db):
    seed(db)
    db.get(Player, 2).name = "TEST Pašalić"
    db.commit()
    response = client.get("/api/report.pdf?left=1&right=2&role=Forward&min_minutes=0")
    text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(response.content)).pages)
    assert "TEST Pašalić" in text


def test_nested_event_validation():
    from app.ingest import SourceEvent

    e = fixture()[3]
    e["shot"]["statsbomb_xg"] = 1.1
    with pytest.raises(ValidationError):
        SourceEvent.model_validate(e)
    e = fixture()[1]
    e.pop("pass")
    with pytest.raises(ValidationError):
        SourceEvent.model_validate(e)


def test_report_capacity_is_bounded(client):
    from app.main import REPORT_SLOTS

    REPORT_SLOTS.acquire()
    REPORT_SLOTS.acquire()
    try:
        response = client.get("/api/report.pdf?left=1&right=2")
        assert response.status_code == 429
        assert response.headers["retry-after"] == "2"
    finally:
        REPORT_SLOTS.release()
        REPORT_SLOTS.release()
