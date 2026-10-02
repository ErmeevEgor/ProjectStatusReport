import json
import unittest
from pathlib import Path

from docx import Document

from project_status_report.render_docx import render_report


ROOT = Path(__file__).resolve().parents[1]


class ReportLayoutTests(unittest.TestCase):
    def test_new_four_section_layout(self):
        data = json.loads(
            (ROOT / "examples" / "sample-report-data.json").read_text(encoding="utf-8")
        )
        temp_root = ROOT / "output" / "test-artifacts"
        temp_root.mkdir(parents=True, exist_ok=True)
        path = temp_root / "layout-clean.docx"
        render_report(data, path, include_comments=False)
        document = Document(path)

        paragraph_text = [paragraph.text for paragraph in document.paragraphs]
        all_text = "\n".join(paragraph_text)
        table_text = "\n".join(
            paragraph.text for table in document.tables
            for row in table.rows for cell in row.cells
            for paragraph in cell.paragraphs
        )
        combined = all_text + "\n" + table_text

        headings = {
            paragraph.text: paragraph.style.name
            for paragraph in document.paragraphs
            if paragraph.text
        }
        self.assertEqual(headings["1. Общие сведения"], "Heading 1")
        self.assertEqual(headings["2. Данные по задачам"], "Heading 1")
        self.assertEqual(headings["3. Риски проекта"], "Heading 1")
        self.assertEqual(headings["4. Ключевые вопросы и проблемы"], "Heading 1")
        self.assertEqual(headings["Сводные данные и общий статус"], "Heading 2")
        self.assertEqual(headings["Общий статус проекта"], "Heading 2")
        self.assertNotIn("ПРОГРЕСС И БЮДЖЕТ", combined)
        self.assertIn("Итоговый прогресс:", all_text)
        self.assertIn("Оперативные факты отчетного периода", all_text)
        self.assertIn(data["operational_items"][0]["title"], table_text)
        self.assertIn(data["report"]["risk_summary"], all_text)
        self.assertIn(data["report"]["next_control_milestone"], all_text)

        passport = document.tables[0]
        self.assertEqual(len(passport.rows), 4)
        self.assertEqual(len(passport.columns), 4)


if __name__ == "__main__":
    unittest.main()
