"""Offline condition-monitoring prototype using synthetic sensor data."""

import csv
import json
import math
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

TEMP_LIMIT = 80.0
VIBRATION_LIMIT = 7.0
MACHINE_IDS = frozenset(f"M-{i:02d}" for i in range(1, 11))


@dataclass(frozen=True)
class Sample:
    machine_id: str
    timestamp: str
    temperature_c: float
    vibration_mm_s: float


def validate(sample: Sample) -> bool:
    """Accept registered machines, finite measurements and UTC timestamps."""
    if not isinstance(sample, Sample) or sample.machine_id not in MACHINE_IDS:
        return False
    if not isinstance(sample.timestamp, str):
        return False
    try:
        stamp = datetime.fromisoformat(sample.timestamp.replace("Z", "+00:00"))
    except ValueError:
        return False
    if stamp.utcoffset() != timedelta(0):
        return False
    values = (sample.temperature_c, sample.vibration_mm_s)
    return all(
        isinstance(value, (float, int))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in values
    )


def detect(sample: Sample) -> list[tuple[str, float]]:
    if not validate(sample):
        raise ValueError("Invalid sensor message")
    alarms = []
    if sample.temperature_c > TEMP_LIMIT:
        alarms.append(("TEMPERATURE", sample.temperature_c))
    if sample.vibration_mm_s > VIBRATION_LIMIT:
        alarms.append(("VIBRATION", sample.vibration_mm_s))
    return alarms


def generate(seed: int = 42, n: int = 100):
    """Produce deterministic test records with consecutive UTC timestamps."""
    if n < 0:
        raise ValueError("Sample count must be nonnegative")
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index in range(n):
        yield Sample(
            machine_id=f"M-{rng.randint(1, 10):02d}",
            timestamp=(start + timedelta(seconds=index)).isoformat(),
            temperature_c=round(rng.uniform(55, 95), 2),
            vibration_mm_s=round(rng.uniform(2, 9), 2),
        )


def database(path: str = ":memory:") -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS samples "
        "(machine_id TEXT, timestamp TEXT, temperature REAL, vibration REAL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS alarms "
        "(machine_id TEXT, timestamp TEXT, kind TEXT, value REAL)"
    )
    return connection


def persist(connection: sqlite3.Connection, sample: Sample) -> list[tuple[str, float]]:
    alarms = detect(sample)
    with connection:
        connection.execute(
            "INSERT INTO samples VALUES (?, ?, ?, ?)",
            (sample.machine_id, sample.timestamp, sample.temperature_c, sample.vibration_mm_s),
        )
        for kind, value in alarms:
            connection.execute(
                "INSERT INTO alarms VALUES (?, ?, ?, ?)",
                (sample.machine_id, sample.timestamp, kind, value),
            )
    return alarms


def export_alarms(connection: sqlite3.Connection, path: str) -> int:
    rows = connection.execute(
        "SELECT machine_id, timestamp, kind, value "
        "FROM alarms ORDER BY timestamp, machine_id, kind"
    ).fetchall()
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["machine_id", "timestamp", "kind", "value"])
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    db = database()
    for reading in generate(n=100):
        persist(db, reading)
    print(json.dumps({
        "mode": "offline-simulation",
        "persisted_samples": db.execute("SELECT COUNT(*) FROM samples").fetchone()[0],
        "alarms": db.execute("SELECT COUNT(*) FROM alarms").fetchone()[0],
        "configured_machines": len(MACHINE_IDS),
    }, indent=2))
    db.close()
