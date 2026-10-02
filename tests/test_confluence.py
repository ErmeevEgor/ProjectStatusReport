from __future__ import annotations

import unittest
from pathlib import Path

from project_status_report.confluence import docx_to_confluence_storage, latest_report_page


ROOT = Path(__file__).resolve().parents[1]


class ConfluenceTests(unittest.TestCase):
    def test_latest_report_uses_update_timestamp(self):
        pages = [
            {"id": "1", "title": "ОСП 1", "version": {"number": 2, "when": "2026-09-01"}},
            {"id": "2", "title": "Шаблон ОСП", "version": {"number": 1, "when": "2026-12-01"}},
            {"id": "3", "title": "ОСП 2", "version": {"number": 1, "when": "2026-10-01"}},
            {"id": "4", "title": "План проекта", "version": {"number": 9, "when": "2026-11-01"}},
        ]
        self.assertEqual(latest_report_page(pages)["id"], "3")

    def test_clean_docx_converts_to_confluence_storage(self):
        docx = ROOT / "output" / "run-2026-10-02" / "deliverables" / "OSP-3-2026-10-02-clean.docx"
        if not docx.exists():
            self.skipTest("Generated OSP smoke fixture is not present")
        storage = docx_to_confluence_storage(docx)
        self.assertIn("<h1>1. Общие сведения</h1>", storage)
        self.assertIn("<table><tbody>", storage)
        self.assertIn("Ключевые вопросы и проблемы", storage)
        self.assertNotIn("comments.xml", storage)


if __name__ == "__main__":
    unittest.main()
