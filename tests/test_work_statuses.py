import unittest
from project_status_report.rules import display_work_status


class WorkStatusTests(unittest.TestCase):
    def test_visible_model_is_four_statuses(self):
        self.assertEqual(display_work_status("Не начато"), "Не начато")
        self.assertEqual(display_work_status("В работе"), "В работе")
        self.assertEqual(display_work_status("На согласовании"), "На согласовании")
        self.assertEqual(display_work_status("Выполнено"), "Выполнено")

    def test_legacy_unconfirmed_status_is_never_visible(self):
        self.assertEqual(display_work_status("Факт не подтвержден"), "Не начато")
        self.assertEqual(display_work_status("Требует подтверждения"), "Не начато")


if __name__ == "__main__":
    unittest.main()
