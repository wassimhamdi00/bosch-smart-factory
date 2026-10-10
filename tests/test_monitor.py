"""Unit tests for the offline monitoring prototype."""

import csv
import json
import math
import os
import tempfile
import unittest

from src.monitor import Sample, database, detect, export_alarms, generate, persist
from src.mqtt_adapter import handle_payload


class MonitorTests(unittest.TestCase):
    @staticmethod
    def sample(t=70.0, v=2.0, machine_id="M-01", timestamp="2026-10-09T12:00:00Z"):
        return Sample(machine_id, timestamp, t, v)

    def test_temperature_boundary(self):
        self.assertEqual(detect(self.sample(t=80.0)), [])
        self.assertEqual(detect(self.sample(t=80.1)), [("TEMPERATURE", 80.1)])

    def test_vibration_boundary(self):
        self.assertEqual(detect(self.sample(v=7.0)), [])
        self.assertEqual(detect(self.sample(v=7.1)), [("VIBRATION", 7.1)])
        self.assertEqual(len(detect(self.sample(t=81.0, v=7.1))), 2)

    def test_invalid_machine(self):
        invalid = [
            self.sample(machine_id="M-99"),
            self.sample(timestamp="not-a-date"),
            self.sample(timestamp="2026-10-09T12:00:00"),
            self.sample(t=math.nan),
            self.sample(v=math.inf),
        ]
        for reading in invalid:
            with self.subTest(reading=reading), self.assertRaises(ValueError):
                detect(reading)

    def test_reproducibility(self):
        a, b = list(generate(seed=42, n=100)), list(generate(seed=42, n=100))
        self.assertEqual(a, b)
        self.assertEqual(len({row.timestamp for row in a}), 100)
        self.assertEqual({row.machine_id for row in a}, {f"M-{n:02d}" for n in range(1, 11)})

    def test_db_and_csv(self):
        db = database()
        persist(db, self.sample(t=82.0))
        self.assertEqual(db.execute("SELECT COUNT(*) FROM alarms").fetchone()[0], 1)
        message = json.dumps({
            "machine_id": "M-02",
            "timestamp": "2026-10-09T12:00:01Z",
            "temperature_c": 65.0,
            "vibration_mm_s": 8.0,
        })
        self.assertEqual(handle_payload(db, message), [("VIBRATION", 8.0)])
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "alarms.csv")
            self.assertEqual(export_alarms(db, path), 2)
            with open(path, encoding="utf-8", newline="") as file:
                self.assertEqual(len(list(csv.reader(file))), 3)
        db.close()


if __name__ == "__main__":
    unittest.main()
