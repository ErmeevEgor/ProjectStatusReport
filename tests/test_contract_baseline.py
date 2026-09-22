import unittest

from project_status_report.rules import calculate_progress, inherit_parent_periods, page2_contractual_rows

from _fixtures import contractual_fixture


class ContractBaselineTests(unittest.TestCase):
    def test_page2_contains_only_seven_contractual_rows(self):
        data = contractual_fixture()
        rows = page2_contractual_rows(data)
        self.assertEqual([row["id"] for row in rows], ["1.1", "1.2", "1.3", "1.4", "1.5", "2.1", "2.2"])
        self.assertTrue(all(row["baseline_kind"] == "contract_task" for row in rows))

    def test_operational_tracker_does_not_become_costing_basis(self):
        result = calculate_progress(contractual_fixture())
        self.assertEqual(result.basis, "tasks")
        self.assertEqual(result.earned, 252000)
        self.assertEqual(result.percent, 36.2)
        self.assertFalse(any(str(item["id"]).startswith("OP-") for item in result.items))

    def test_unambiguous_parent_period_is_inherited(self):
        data = inherit_parent_periods(contractual_fixture())
        task = next(item for item in data["tasks"] if item["id"] == "1.1")
        self.assertEqual(task["planned_start"], "2026-08-27")
        self.assertEqual(task["planned_end"], "2026-09-14")
        self.assertEqual(task["date_basis"], "parent_stage_period")

    def test_parent_and_children_are_not_double_counted(self):
        data = contractual_fixture()
        data["tasks"] = data["stages"] + data["tasks"]
        rows = page2_contractual_rows(data)
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row["budget"] for row in rows), 696000)


if __name__ == "__main__":
    unittest.main()
