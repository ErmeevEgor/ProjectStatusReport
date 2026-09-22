import unittest

from project_status_report.rules import calculate_progress


class ProgressTests(unittest.TestCase):
    def test_weighted_progress_by_task_budget(self):
        data = {
            "approved_budget": 100000,
            "tasks": [
                {"id": "1", "title": "A", "status": "Выполнено", "budget": 40000},
                {"id": "2", "title": "B", "status": "На согласовании", "budget": 20000},
                {"id": "3", "title": "C", "status": "В работе", "budget": 30000},
                {"id": "4", "title": "D", "status": "Не начато", "budget": 10000},
            ],
            "stages": [],
        }
        result = calculate_progress(data)
        self.assertEqual(result.basis, "tasks")
        self.assertEqual(result.earned, 73000)
        self.assertEqual(result.percent, 73.0)

    def test_falls_back_to_stage_costing(self):
        data = {
            "approved_budget": 100000,
            "tasks": [{"id": "1.1", "title": "A", "status": "Выполнено", "budget": None}],
            "stages": [{"id": "S1", "title": "Stage 1", "status": "В работе", "budget": 100000}],
        }
        result = calculate_progress(data)
        self.assertEqual(result.basis, "stages")
        self.assertEqual(result.percent, 50.0)

    def test_operational_items_are_ignored_even_if_their_sum_matches_budget(self):
        data = {
            "approved_budget": 100000,
            "tasks": [
                {"id": "OP-1", "title": "Backlog A", "status": "Выполнено", "budget": 50000,
                 "baseline_kind": "operational"},
                {"id": "OP-2", "title": "Backlog B", "status": "Выполнено", "budget": 50000,
                 "baseline_kind": "operational"},
            ],
            "stages": [
                {"id": "S1", "title": "Contract stage", "status": "В работе", "budget": 100000,
                 "baseline_kind": "contract_stage"}
            ],
        }
        result = calculate_progress(data)
        self.assertEqual(result.basis, "stages")
        self.assertEqual(result.percent, 50.0)

    def test_rejects_incomplete_costing(self):
        data = {
            "approved_budget": 100000,
            "tasks": [{"id": "1", "title": "A", "status": "Выполнено", "budget": 20000}],
            "stages": [{"id": "S1", "title": "Stage 1", "status": "В работе", "budget": 50000}],
        }
        with self.assertRaises(ValueError):
            calculate_progress(data)


if __name__ == "__main__":
    unittest.main()
