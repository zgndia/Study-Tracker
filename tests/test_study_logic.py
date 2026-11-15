import unittest

from stdt.study_logic import get_daily_target, get_days_to_target, get_study_goals


class StudyLogicTests(unittest.TestCase):
    def test_compound_progression_stops_at_first_target_day(self):
        self.assertEqual(get_daily_target(1), 28)
        final_day = get_days_to_target()
        self.assertEqual(get_daily_target(final_day), 360)
        self.assertLess(get_daily_target(final_day - 1), 360)
        self.assertEqual(final_day, 45)

    def test_progression_is_clamped(self):
        self.assertEqual(get_daily_target(0), 28)
        self.assertEqual(get_daily_target(61), 360)

    def test_day_one_goals(self):
        self.assertEqual(get_study_goals(1), (15, 5, 13, 28))

    def test_custom_ceiling(self):
        self.assertEqual(get_daily_target(60, target_minutes=480), 480)
        self.assertEqual(get_daily_target(1, target_minutes=20), 20)

    def test_higher_rate_never_produces_less_study_time(self):
        for day in range(1, 100):
            self.assertGreaterEqual(
                get_daily_target(day, rate=0.10),
                get_daily_target(day, rate=0.05),
            )

    def test_rate_controls_target_day(self):
        self.assertLess(get_days_to_target(rate=0.10), get_days_to_target(rate=0.05))
        self.assertEqual(get_days_to_target(target_minutes=360, rate=0.057), 48)

    def test_six_hour_goal_has_four_hours_lecture_and_100_questions(self):
        self.assertEqual(get_study_goals(60), (240, 100, 120, 360))


if __name__ == "__main__":
    unittest.main()
