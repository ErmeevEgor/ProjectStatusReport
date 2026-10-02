import unittest

from project_status_report.rules import resolve_payment_display


class PaymentEvidenceTests(unittest.TestCase):
    def test_official_is_paid(self):
        payment = {
            "fact_evidence_level": "official",
            "actual_text": "Поступление по выписке",
            "actual_date": "2026-09-04",
            "status": "Требует подтверждения",
        }
        result = resolve_payment_display(payment, "2026-09-21")
        self.assertEqual(result.status, "Оплачен")
        self.assertEqual(result.actual_date, "2026-09-04")

    def test_project_confirmed_is_confirmed_without_inventing_date(self):
        payment = {
            "fact_evidence_level": "project_confirmed",
            "actual_date": None,
            "status": "Требует подтверждения",
        }
        result = resolve_payment_display(payment, "2026-09-21")
        self.assertEqual(result.actual_text, "Факт поступления подтвержден")
        self.assertEqual(result.status, "Подтвержден")
        self.assertIsNone(result.actual_date)

    def test_provisional_requires_confirmation(self):
        result = resolve_payment_display(
            {"fact_evidence_level": "provisional", "actual_date": None},
            "2026-09-21",
        )
        self.assertEqual(result.status, "Требует подтверждения")
        self.assertIsNone(result.actual_date)

    def test_missing_before_deadline_is_not_due(self):
        result = resolve_payment_display(
            {
                "fact_evidence_level": "missing",
                "planned_date": "2026-10-10",
                "actual_date": None,
            },
            "2026-09-21",
        )
        self.assertEqual(result.status, "Не наступил срок")
        self.assertEqual(result.actual_text, "—")
        self.assertIsNone(result.actual_date)

    def test_legacy_json_remains_supported(self):
        result = resolve_payment_display(
            {"status": "Оплачен", "actual_date": "2026-09-04"},
            "2026-09-21",
        )
        self.assertEqual(result.status, "Оплачен")


if __name__ == "__main__":
    unittest.main()

