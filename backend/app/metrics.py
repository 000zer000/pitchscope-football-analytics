"""Pure transformations: elapsed period clocks including stoppage, excluding shootouts."""

from collections import defaultdict

TRANSFORM_VERSION = "1.2.0"


def seconds(timestamp):
    h, m, s = timestamp.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def role_group(position):
    if "Goalkeeper" in position:
        return "Goalkeeper"
    if "Back" in position:
        return "Defender"
    if "Midfield" in position:
        return "Midfielder"
    return "Forward"


def reconstruct(events, lineups=None):
    entry_positions = {
        p["player_id"]: p["positions"][0]["position"]
        for team in (lineups or [])
        for p in team["lineup"]
        if p.get("positions")
    }
    ends = defaultdict(list)
    periods = sorted({e["period"] for e in events if e["period"] <= 4})
    for e in events:
        if e["type"]["name"] == "Half End" and e["period"] <= 4:
            ends[e["period"]].append(seconds(e["timestamp"]))
    reliable_clock = periods in ([1, 2], [1, 2, 3, 4])
    durations = {}
    for p in periods:
        if not ends[p] or max(ends[p]) - min(ends[p]) > 1:
            reliable_clock = False
        durations[p] = max(ends[p], default=0)
    offsets = {p: sum(durations[k] for k in periods if k < p) for p in periods}
    duration = sum(durations.values())
    players, active, suspended, elapsed, issues = {}, {}, {}, defaultdict(float), {}

    def close(pid, t):
        if pid in active:
            elapsed[pid] += max(0, t - active.pop(pid))
        else:
            issues[pid] = "Exit without a matching entry"

    def enter(pid, team, pos, t):
        pos = entry_positions.get(pid, pos)
        if pid in active:
            issues[pid] = "Inconsistent overlapping presence"
        players.setdefault(pid, {"player_id": pid, "team_id": team, "position": pos, "role": role_group(pos)})
        active[pid] = t

    for e in sorted(events, key=lambda e: e["index"]):
        if e["period"] > 4:
            continue
        t = offsets[e["period"]] + seconds(e["timestamp"])
        kind = e["type"]["name"]
        pid = e.get("player", {}).get("id")
        team = e["team"]["id"]
        if seconds(e["timestamp"]) > durations[e["period"]] + 1:
            reliable_clock = False
        if kind == "Starting XI":
            for item in e["tactics"]["lineup"]:
                enter(item["player"]["id"], team, item["position"]["name"], 0)
        elif kind == "Substitution":
            if pid in suspended:
                suspended.pop(pid)
            else:
                close(pid, t)
            replacement = e["substitution"]["replacement"]["id"]
            enter(replacement, team, e.get("position", {}).get("name", "Unknown"), t)
        elif kind == "Player Off":
            if pid in active:
                close(pid, t)
                suspended[pid] = True
            else:
                issues[pid] = "Inconsistent temporary exit"
        elif kind == "Player On":
            if pid in suspended:
                active[pid] = t
                suspended.pop(pid)
            else:
                issues[pid] = "Return without a temporary exit"
        card = e.get("bad_behaviour", e.get("foul_committed", {})).get("card", {}).get("name")
        if card in ("Red Card", "Second Yellow"):
            if pid in active:
                close(pid, t)
            elif pid not in suspended:
                issues[pid] = "Dismissal without an active appearance"
            suspended.pop(pid, None)
        if pid and kind in ("Pass", "Shot") and pid in players and pid not in active:
            issues[pid] = "Event outside reconstructed presence"
        if pid and kind in ("Pass", "Shot") and pid not in players:
            enter(pid, team, e.get("position", {}).get("name", "Unknown"), t)
            issues[pid] = "Entry missing from events"
    for pid in list(active):
        close(pid, duration)
    for pid, row in players.items():
        issue = issues.get(pid) if reliable_clock else "Missing or inconsistent period end"
        row.update(
            minutes=None if issue else elapsed[pid] / 60,
            uncertainty=issue,
            shots=0,
            goals=0,
            xg=0.0,
            xg_missing=0,
            passes=0,
            completed=0,
            penalties=0,
        )
    for e in events:
        pid = e.get("player", {}).get("id")
        if e["period"] > 4 or pid not in players:
            continue
        row = players[pid]
        if e["type"]["name"] == "Shot":
            shot = e["shot"]
            row["shots"] += 1
            row["goals"] += shot["outcome"]["name"] == "Goal"
            row["penalties"] += shot.get("type", {}).get("name") == "Penalty"
            if shot.get("statsbomb_xg") is None:
                row["xg_missing"] += 1
            else:
                row["xg"] += shot["statsbomb_xg"]
        if e["type"]["name"] == "Pass":
            row["passes"] += 1
            row["completed"] += "outcome" not in e["pass"]
    for row in players.values():
        if row["xg_missing"]:
            row["xg"] = None
    return list(players.values()), durations, duration / 60 if reliable_clock else None
