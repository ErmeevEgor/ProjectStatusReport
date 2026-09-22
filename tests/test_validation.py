import unittest

from project_status_report.rules import inherit_parent_periods
from project_status_report.validation import validate_report

from _fixtures import valid_covered_fixture


class ValidationTests(unittest.TestCase):
    def test_page2_requires_contractual_source(self):
        data = valid_covered_fixture()
        data["tasks"][0]["plan_source_type"] = "other"
        data["tasks"][0]["sources"] = ["tracker"]
        result = validate_report(inherit_parent_periods(data))
        self.assertTrue(any("not supported by contractual baseline" in error for error in result.errors))

    def test_operational_row_in_tasks_is_error_and_not_costed(self):
        data = valid_covered_fixture()
        data["tasks"].append(data["operational_items"][0])
        result = validate_report(inherit_parent_periods(data))
        self.assertTrue(any("baseline_kind=operational" in error for error in result.errors))

    def test_page2_budget_must_cover_approved_budget(self):
        data = valid_covered_fixture()
        data["tasks"][0]["budget"] -= 100
        data["stages"] = []
        result = validate_report(inherit_parent_periods(data))
        self.assertTrue(any("complete contractual progress basis" in error for error in result.errors))

    def test_health_check_7_must_match_open_risks(self):
        data = valid_covered_fixture()
        data["health_check"][1]["answer"] = "Нет"
        result = validate_report(inherit_parent_periods(data))
        self.assertTrue(any("Health check #7" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
