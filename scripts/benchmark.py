"""Sequential localhost HTTP timings; no claims about production throughput."""

import json
import os
import platform
import statistics
import time
from pathlib import Path

import httpx

base = os.getenv("BENCHMARK_URL", "http://127.0.0.1:8000")
paths = [
    "/api/coverage",
    "/api/players?role=Forward&min_minutes=180",
    "/api/compare?left=5503&right=3009&role=Forward&min_minutes=180",
    "/api/matches/3869685/events?kind=Shot&size=100",
    "/api/report.pdf?left=5503&right=3009&role=Forward&min_minutes=180",
]
with httpx.Client(base_url=base, timeout=60) as client:
    coverage = client.get("/api/coverage").json()
    results = []
    for path in paths:
        for _ in range(2):
            client.get(path).raise_for_status()
        elapsed = []
        for _ in range(10):
            start = time.perf_counter()
            response = client.get(path)
            response.raise_for_status()
            elapsed.append((time.perf_counter() - start) * 1000)
        results.append(
            {
                "path": path,
                "attempts": 10,
                "warmups": 2,
                "median_ms": round(statistics.median(elapsed), 2),
                "min_ms": round(min(elapsed), 2),
                "max_ms": round(max(elapsed), 2),
                "last_bytes": len(response.content),
            }
        )
report = {
    "machine": {
        "system": platform.system(),
        "architecture": platform.machine(),
        "logical_cpus": os.cpu_count(),
    },
    "database": "PGlite PostgreSQL 18.6, single connection, WebAssembly; native PostgreSQL not measured",
    "dataset": {k: coverage[k] for k in ["imported_matches", "events", "players", "source_commit"]},
    "method": "Sequential HTTP localhost, persistent client, 2 warmups then 10 attempts. API and DB warm. No concurrent requests.",
    "results": results,
}
Path("docs/benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
