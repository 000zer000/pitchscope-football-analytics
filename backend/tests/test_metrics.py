from copy import deepcopy

import pytest
from app.metrics import POSITION_ROLES, reconstruct, role_group
from fixtures import event, fixture


def by_id(events):
    return {r["player_id"]: r for r in reconstruct(events)[0]}


@pytest.mark.parametrize("position", [None, "", "Unknown", "Unrecognised position", "New Back Role"])
def test_unknown_position_never_defaults_to_forward(position):
    assert role_group(position) == "Unknown"


@pytest.mark.parametrize("position,role", list(POSITION_ROLES.items()))
def test_explicit_position_contract(position, role):
    assert role_group(position) == role


def test_missing_replacement_role_preserves_minutes_and_unknown_role():
    events = deepcopy(fixture())
    for e in events:
        if e["type"]["name"] == "Substitution":
            e.pop("position", None)
    row = by_id(events)[2]
    assert row["position"] == "Unknown" and row["role"] == "Unknown"
    assert row["minutes"] == 33


def test_minutes_substitution_and_weighted_components():
    rows, periods, duration = reconstruct(fixture())
    a, b, g = [by_id(fixture())[i] for i in (1, 2, 3)]
    assert periods == {1: 2820, 2: 2880}
    assert duration == 95
    assert a["minutes"] == 62  # 47 + 15, not the nominal minute 60
    assert b["minutes"] == 33
    assert g["minutes"] == 95
    assert (a["passes"], a["completed"], a["shots"], a["goals"], a["penalties"], a["xg"]) == (
        2,
        1,
        1,
        1,
        1,
        0.75,
    )


def test_extra_time_shootout_and_own_goal():
    events = fixture() + [
        event(10, "Half End", 3, "00:16:00.000"),
        event(11, "Half End", 4, "00:17:00.000"),
        event(
            12,
            "Shot",
            5,
            "00:01:00.000",
            2,
            shot={"outcome": {"name": "Goal"}, "type": {"name": "Penalty"}, "statsbomb_xg": 0.8},
        ),
        event(13, "Own Goal Against", 4, "00:16:00.000", 2),
    ]
    assert reconstruct(events)[2] == 128
    assert by_id(events)[2]["minutes"] == 66
    assert by_id(events)[2]["goals"] == 0
    assert by_id(events)[2]["xg"] == 0.25
    assert by_id(events)[2]["shots"] == 1


@pytest.mark.parametrize("card", ["Red Card", "Second Yellow"])
def test_red_and_second_yellow(card):
    events = fixture() + [
        event(10, "Bad Behaviour", 2, "00:25:00.000", 2, bad_behaviour={"card": {"name": card}})
    ]
    events[-1]["index"] = 8.5
    assert by_id(events)[2]["minutes"] == 10


def test_foul_card_temporary_exit_and_halftime_change():
    events = fixture() + [
        event(10, "Player Off", 2, "00:05:00.000", 1),
        event(11, "Player On", 2, "00:07:00.000", 1),
        event(12, "Foul Committed", 2, "00:30:00.000", 2, foul_committed={"card": {"name": "Red Card"}}),
    ]
    events[-3]["index"] = 5.2
    events[-2]["index"] = 5.3
    events[-1]["index"] = 8.5
    assert by_id(events)[1]["minutes"] == 60
    assert by_id(events)[2]["minutes"] == 15
    half = fixture()
    half[5]["timestamp"] = "00:00:00.000"
    assert by_id(half)[1]["minutes"] == 47
    assert by_id(half)[2]["minutes"] == 48


def test_missing_clock_or_entry_not_imputed():
    e = [e for e in fixture() if not (e["type"]["name"] == "Half End" and e["period"] == 2)]
    assert all(p["minutes"] is None for p in reconstruct(e)[0])
    e = [e for e in fixture() if e["type"]["name"] != "Substitution"]
    assert by_id(e)[2]["minutes"] is None
    assert by_id(e)[2]["uncertainty"]


def test_missing_xg_not_zero():
    e = deepcopy(fixture())
    e[3]["shot"].pop("statsbomb_xg")
    assert by_id(e)[1]["xg"] is None
    assert by_id(e)[1]["xg_missing"] == 1


def test_lineup_role_and_missing_return():
    lineups = [{"lineup": [{"player_id": 2, "positions": [{"position": "Center Midfield"}]}]}]
    rows = {r["player_id"]: r for r in reconstruct(fixture(), lineups)[0]}
    assert rows[2]["role"] == "Midfielder"
    e = fixture() + [event(10, "Player Off", 2, "00:16:30.000", 2)]
    e[-1]["index"] = 7.5
    assert by_id(e)[2]["minutes"] is None
