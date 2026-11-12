import unittest

from stdt.study_logic import get_daily_target, get_study_goals


class StudyLogicTests(unittest.TestCase):
    def test_progression_endpoints(self):
        self.assertEqual(get_daily_target(1), 28)
        self.assertEqual(get_daily_target(60), 360)

    def test_progression_is_clamped(self):
        self.assertEqual(get_daily_target(0), 28)
        self.assertEqual(get_daily_target(61), 360)

    def test_day_one_goals(self):
        self.assertEqual(get_study_goals(1), (15, 5, 13, 28))


if __name__ == "__main__":
    unittest.main()
