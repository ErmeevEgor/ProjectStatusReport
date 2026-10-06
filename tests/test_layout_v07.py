import json
import unittest
from pathlib import Path

from docx import Document

from project_status_report.layout_v07 import render_report

ROOT = Path(__file__).resolve().parents[1]


class LayoutV07Tests(unittest.TestCase):
    def test_page2_uses_stable_task_columns_for_contractual_rows(self):
        data = json.loads((ROOT / "examples" / "sample-report-data.json").read_text(encoding="utf-8"))

        # The sample intentionally has tasks=[]; page 2 therefore uses costed
        # contractual stages.  This guards both supported baseline shapes.
        data["stages"][0]["title"] = "Контроль срока действия договора"
        data["stages"][0]["result"] = "Реализация и сдача разработанного функционала"

        temp_root = ROOT / "output" / "test-artifacts"
        temp_root.mkdir(parents=True, exist_ok=True)
        path = temp_root / "layout-v07.docx"
        render_report(data, path, include_comments=False)
        document = Document(path)

        expected = [
            "Код задачи", "Наименование", "Задача", "Статус", "Бюджет",
            "Освоено", "План начала", "План завершения", "Факт", "Комментарий",
        ]
        task_table = None
        for table in document.tables:
            headers = [cell.text for cell in table.rows[0].cells]
            if headers == expected:
                task_table = table
                break

        self.assertIsNotNone(task_table)
        text = "\n".join(cell.text for row in task_table.rows[1:] for cell in row.cells)
        self.assertIn("Контроль срока действия договора", text)
        self.assertIn("Реализация и сдача разработанного функционала", text)


if __name__ == "__main__":
    unittest.main()
