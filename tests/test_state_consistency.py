import unittest

from project_status_report.validation import validate_report

from _fixtures import valid_covered_fixture


class StateConsistencyTests(unittest.TestCase):
    def _with_confirmed_advance(self):
        data = valid_covered_fixture()
        data["payments"] = [
            {
                "id": "ADVANCE",
                "name": "Аванс",
                "amount": data["approved_budget"],
                "plan_basis": "По договору",
                "planned_date": "2026-09-01",
                "actual_text": None,
                "actual_date": None,
                "status": "Подтвержден",
                "fact_evidence_level": "project_confirmed",
                "sources": ["tracker"],
            }
        ]
        return data

    def test_confirmed_payment_cannot_keep_confirmation_open_item(self):
        data = self._with_confirmed_advance()
        data["open_items"] = [
            {
                "id": "PAY-1",
                "priority": "low",
                "item": "Подтвердить фактический статус авансовой оплаты",
                "required_action": "Получить подтверждение и урегулировать расхождение суммы",
                "owner": "Исполнитель",
                "due_date": "2026-09-22",
                "status": "Открыт",
                "sources": ["tracker"],
            }
        ]
        result = validate_report(data)
        self.assertTrue(any("already confirmed payment" in error for error in result.errors))
        self.assertTrue(any("Compound open item" in error for error in result.errors))

    def test_only_amount_discrepancy_may_remain(self):
        data = self._with_confirmed_advance()
        data["open_items"] = [
            {
                "id": "PAY-2",
                "priority": "low",
                "item": "Урегулировать расхождение суммы авансового счета",
                "required_action": "Согласовать перенос разницы в финальный счет",
                "owner": "Исполнитель",
                "due_date": "2026-09-22",
                "status": "Открыт",
                "risk_impact": "none",
                "risk_impact_reason": "Не влияет на срок или объем работ.",
                "sources": ["tracker"],
            }
        ]
        result = validate_report(data)
        self.assertFalse(any("State consistency" in error for error in result.errors))
        self.assertFalse(any("Compound open item" in error for error in result.errors))

    def test_open_technical_problem_requires_health_check_5_yes(self):
        data = valid_covered_fixture()
        data["risks"].append(
            {
                "id": "P-TECH",
                "date": "2026-09-21",
                "type": "ПРОБЛЕМА",
                "title": "Технический сбой интеграции",
                "probability_or_fact": "Реализовано",
                "impact_degree": "Средняя",
                "impact": "Недоступна передача данных.",
                "actions": "Устранить ошибку.",
                "result": None,
                "status": "Открыт",
                "related_task_ids": [],
                "related_open_item_ids": [],
                "materiality": "medium",
                "sources": ["tracker"],
            }
        )
        data["health_check"].append(
            {
                "number": 5,
                "question": "Есть технические проблемы?",
                "answer": "Нет",
                "comment": None,
                "sources": [],
            }
        )
        result = validate_report(data)
        self.assertTrue(any("Health check #5" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()

