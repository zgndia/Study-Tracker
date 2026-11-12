import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from stdt.storage import load_start_date, save_start_date


class StorageTests(unittest.TestCase):
    def test_round_trip_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            save_start_date(date(2026, 11, 12), path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"start_date": "2026-11-12"})
            self.assertEqual(load_start_date(path), date(2026, 11, 12))

    def test_missing_file_initializes_today(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            self.assertEqual(load_start_date(path), date.today())
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
