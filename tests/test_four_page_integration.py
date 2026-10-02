import json
import shutil
import subprocess
import unittest
from pathlib import Path

from project_status_report.render_docx import render_report


ROOT = Path(__file__).resolve().parents[1]


class FourPageIntegrationTests(unittest.TestCase):
    def test_clean_docx_renders_to_exactly_four_pages_when_libreoffice_is_available(self):
        soffice = shutil.which("soffice") or shutil.which("soffice.exe")
        pdfinfo = shutil.which("pdfinfo") or shutil.which("pdfinfo.exe")
        if not soffice or not pdfinfo:
            self.skipTest("LibreOffice/Poppler integration tools are not available on PATH")

        data = json.loads(
            (ROOT / "examples" / "sample-report-data.json").read_text(encoding="utf-8")
        )
        temp = ROOT / "output" / "test-artifacts" / "four-page"
        temp.mkdir(parents=True, exist_ok=True)
        docx_path = temp / "clean.docx"
        render_report(data, docx_path, include_comments=False)
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(temp), str(docx_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        result = subprocess.run(
            [pdfinfo, str(temp / "clean.pdf")],
            check=True,
            capture_output=True,
            text=True,
        )
        pages = next(
            int(line.split(":", 1)[1].strip())
            for line in result.stdout.splitlines()
            if line.startswith("Pages:")
        )
        self.assertEqual(pages, 4)


if __name__ == "__main__":
    unittest.main()
