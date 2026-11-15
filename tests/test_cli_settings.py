import json
import tempfile
import unittest
from pathlib import Path

from stdt.cli import build_parser, parse_duration, parse_rate, parse_setting_overrides
from stdt.storage import load_settings, save_settings


class SettingParserTests(unittest.TestCase):
    def test_rate_formats(self):
        self.assertEqual(parse_rate("10%"), 0.1)
        self.assertEqual(parse_rate("0.1"), 0.1)

    def test_duration_formats(self):
        self.assertEqual(parse_duration("6h"), 360)
        self.assertEqual(parse_duration("6h 30m"), 390)
        self.assertEqual(parse_duration("6h, 30m"), 390)
        self.assertEqual(parse_duration("30m"), 30)

    def test_multiple_overrides(self):
        parsed = parse_setting_overrides(["rate=10%,", "target=6h"])
        self.assertEqual(parsed, {"rate": 0.1, "target_minutes": 360})

    def test_duration_with_internal_comma(self):
        parsed = parse_setting_overrides(["target=6h, 30m", "rate=5%"])
        self.assertEqual(parsed, {"target_minutes": 390, "rate": 0.05})

    def test_cli_accepts_edit_and_preview_arguments(self):
        edit_args = build_parser().parse_args(["-e", "rate=10%,", "target=6h"])
        self.assertEqual(edit_args.edit, ["rate=10%,", "target=6h"])
        preview_args = build_parser().parse_args(["--preview", "target=6h", "rate=5%"])
        self.assertEqual(preview_args.preview, ["target=6h", "rate=5%"])


class SettingsStorageTests(unittest.TestCase):
    def test_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = {"rate": 0.1, "target_minutes": 390}
            save_settings(settings, path)
            self.assertEqual(load_settings(path), settings)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["target_minutes"], 390)

    def test_missing_settings_use_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                load_settings(Path(directory) / "missing.json"),
                {"rate": 0.06, "target_minutes": 360},
            )


if __name__ == "__main__":
    unittest.main()
