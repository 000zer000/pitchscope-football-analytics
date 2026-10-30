"""Original synthetic fixtures, no StatsBomb data redistributed."""


def event(i, kind, period=1, stamp="00:00:00.000", pid=None, **extra):
    row = {
        "id": f"test-{i}",
        "index": i,
        "period": period,
        "timestamp": stamp,
        "minute": int(stamp.split(":")[1]) + {1: 0, 2: 45, 3: 90, 4: 105, 5: 120}[period],
        "second": int(float(stamp.split(":")[2])),
        "type": {"id": i, "name": kind},
        "team": {"id": 100, "name": "Synthetic FC"},
    }
    if pid:
        row["player"] = {
            "id": pid,
            "name": {1: "TEST Alpha", 2: "TEST Beta", 3: "TEST Gamma"}.get(pid, "TEST Player"),
        }
        row["position"] = {"id": 23, "name": "Center Forward"}
    return {**row, **extra}


def fixture():
    return [
        event(
            1,
            "Starting XI",
            tactics={
                "lineup": [
                    {
                        "player": {"id": 1, "name": "TEST Alpha"},
                        "position": {"id": 23, "name": "Center Forward"},
                    },
                    {"player": {"id": 3, "name": "TEST Gamma"}, "position": {"id": 1, "name": "Goalkeeper"}},
                ]
            },
        ),
        event(2, "Pass", stamp="00:10:00.000", pid=1, **{"pass": {}}),
        event(3, "Pass", stamp="00:11:00.000", pid=1, **{"pass": {"outcome": {"name": "Incomplete"}}}),
        event(
            4,
            "Shot",
            stamp="00:12:00.000",
            pid=1,
            location=[110, 40],
            shot={"outcome": {"name": "Goal"}, "type": {"name": "Penalty"}, "statsbomb_xg": 0.75},
        ),
        event(5, "Half End", stamp="00:47:00.000"),
        event(
            6,
            "Substitution",
            period=2,
            stamp="00:15:00.000",
            pid=1,
            substitution={"replacement": {"id": 2, "name": "TEST Beta"}},
        ),
        event(7, "Pass", period=2, stamp="00:16:00.000", pid=2, **{"pass": {}}),
        event(
            8,
            "Shot",
            period=2,
            stamp="00:17:00.000",
            pid=2,
            location=[100, 35],
            shot={"outcome": {"name": "Saved"}, "type": {"name": "Open Play"}, "statsbomb_xg": 0.25},
        ),
        event(9, "Half End", period=2, stamp="00:48:00.000"),
    ]


def meta(mid=10001):
    return {
        "match_id": mid,
        "home_team": {"home_team_id": 100, "home_team_name": "Synthetic FC"},
        "away_team": {"away_team_id": 200, "away_team_name": "Fixture United"},
        "home_score": 1,
        "away_score": 0,
        "match_date": "2022-12-18",
        "competition_stage": {"name": "SYNTHETIC TEST ONLY"},
    }


def lineups():
    return [
        {
            "lineup": [
                {"player_id": 1, "player_name": "TEST Alpha"},
                {"player_id": 2, "player_name": "TEST Beta"},
                {"player_id": 3, "player_name": "TEST Gamma"},
            ]
        },
        {"lineup": []},
    ]
