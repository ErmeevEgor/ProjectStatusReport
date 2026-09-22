import unittest

from project_status_report.rules import inherit_parent_periods
from project_status_report.validation import validate_report

from _fixtures import contractual_fixture, valid_covered_fixture


class RiskCoverageTests(unittest.TestCase):
    def test_overdue_incomplete_task_without_risk_is_error(self):
        result = validate_report(inherit_parent_periods(contractual_fixture()))
        self.assertTrue(any("Overdue incomplete contractual task" in error for error in result.errors))

    def test_overdue_tasks_with_risk_links_are_covered(self):
        result = validate_report(inherit_parent_periods(valid_covered_fixture()))
        self.assertFalse(any("Overdue incomplete contractual task" in error for error in result.errors))

    def test_completed_overdue_task_needs_no_open_risk(self):
        data = contractual_fixture()
        for task in data["tasks"]:
            if task["contract_parent_id"] == "1":
                task["status"] = "Выполнено"
        result = validate_report(inherit_parent_periods(data))
        self.assertFalse(any("Overdue incomplete contractual task" in error for error in result.errors))

    def test_previous_open_risk_requires_reconciliation(self):
        data = valid_covered_fixture()
        data["previous_risks"] = [{"id": "OLD-1", "title": "Старый риск", "status": "Открыт", "sources": []}]
        result = validate_report(inherit_parent_periods(data))
        self.assertTrue(any("no reconciliation result" in error for error in result.errors))
        data["risk_reconciliation"] = [
            {"previous_risk_id": "OLD-1", "result": "transformed", "current_risk_id": "R1", "sources": ["tracker"]}
        ]
        result = validate_report(inherit_parent_periods(data))
        self.assertFalse(any("no reconciliation result" in error for error in result.errors))

    def test_material_open_item_requires_impact_link(self):
        data = valid_covered_fixture()
        data["open_items"] = [
            {
                "id": "Q04", "priority": "high", "item": "Когда будет завершено наполнение НСИ?",
                "required_action": "Завершить НСИ первой волны", "owner": "Заказчик",
                "due_date": "2026-09-22", "status": "Открыт", "sources": ["tracker"],
            }
        ]
        result = validate_report(data)
        self.assertTrue(any("Material open item requires risk coverage" in error for error in result.errors))
        data["risks"][0]["related_open_item_ids"] = ["Q04"]
        result = validate_report(data)
        self.assertFalse(any("Material open item requires risk coverage" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
