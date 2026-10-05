import json
import re
import shutil
import subprocess
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from project_status_report.render_docx import render_report


ROOT = Path(__file__).resolve().parents[1]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ConfluenceCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_root = ROOT / "output" / "test-artifacts"
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.path = self.temp_root / "confluence-clean.docx"
        data = json.loads(
            (ROOT / "examples" / "sample-report-data.json").read_text(encoding="utf-8")
        )
        render_report(data, self.path, include_comments=False)

    def _document_root(self):
        with zipfile.ZipFile(self.path) as archive:
            return ET.fromstring(archive.read("word/document.xml"))

    def test_clean_openxml_is_confluence_safe(self):
        root = self._document_root()
        xml = ET.tostring(root, encoding="unicode")

        self.assertNotIn("txbxContent", xml)
        self.assertNotIn(f"{W}pict", xml)
        fills = {
            node.get(f"{W}fill", "").upper()
            for node in root.findall(f".//{W}shd")
        }
        self.assertTrue(fills <= {"E7E6E6"})

        tables = root.findall(f".//{W}tbl")
        table_descendants = {
            id(nested)
            for table in tables
            for nested in table.findall(f".//{W}tbl")
            if nested is not table
        }
        self.assertFalse(table_descendants)
        self.assertTrue(all(len(table.findall(f".//{W}tc")) > 1 for table in tables))

        colors = {
            color.get(f"{W}val", "").upper()
            for color in root.findall(f".//{W}color")
        }
        self.assertTrue(colors <= {"", "000000", "AUTO"})

    def test_sections_use_real_headings_and_callouts_are_paragraphs(self):
        root = self._document_root()
        table_paragraphs = {
            id(paragraph)
            for table in root.findall(f".//{W}tbl")
            for paragraph in table.findall(f".//{W}p")
        }
        outside = []
        heading_styles = {}
        for paragraph in root.findall(f".//{W}p"):
            text = "".join(node.text or "" for node in paragraph.findall(f".//{W}t"))
            properties = paragraph.find(f"{W}pPr")
            style = None
            if properties is not None:
                style_node = properties.find(f"{W}pStyle")
                if style_node is not None:
                    style = style_node.get(f"{W}val")
            if text:
                heading_styles[text] = style
                if id(paragraph) not in table_paragraphs:
                    outside.append(text)

        for title in (
            "1. Общие сведения",
            "2. Данные по задачам",
            "3. Риски проекта",
            "4. Ключевые вопросы и проблемы",
        ):
            self.assertEqual(heading_styles.get(title), "Heading1")

        outside_text = "\n".join(outside)
        self.assertIn("Ключевой вывод по рискам", outside_text)
        self.assertIn("Финансовое наблюдение", outside_text)
        self.assertIn("Следующий контрольный ориентир:", outside_text)

    def test_working_keeps_source_comments_and_clean_does_not(self):
        data = json.loads(
            (ROOT / "examples" / "sample-report-data.json").read_text(encoding="utf-8")
        )
        working = self.temp_root / "confluence-working.docx"
        render_report(data, working, include_comments=True)
        with zipfile.ZipFile(working) as archive:
            self.assertIn("word/comments.xml", archive.namelist())
        with zipfile.ZipFile(self.path) as archive:
            self.assertNotIn("word/comments.xml", archive.namelist())

    def test_optional_docx_to_html_smoke(self):
        soffice = shutil.which("soffice") or shutil.which("soffice.exe")
        if not soffice:
            self.skipTest("LibreOffice is not available on PATH")
        out_dir = self.temp_root / "html"
        out_dir.mkdir(exist_ok=True)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "html", "--outdir", str(out_dir), str(self.path)],
            check=True,
            capture_output=True,
            text=True,
        )
        html_path = out_dir / "clean.html"
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        self.assertRegex(html, re.compile(r"<h[1-3][^>]*>.*Общие сведения", re.I | re.S))
        self.assertRegex(html, re.compile(r"<p[^>]*>.*Ключевой вывод по рискам", re.I | re.S))


if __name__ == "__main__":
    unittest.main()
