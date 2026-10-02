from __future__ import annotations

import json
import unittest
from pathlib import Path

from project_status_report.cli import main


ROOT = Path(__file__).resolve().parents[1]


class ExternalStateTests(unittest.TestCase):
    def test_state_json_is_separated_from_docx_output(self):
        root = ROOT / "output" / "test-artifacts" / "external-state"
        output_dir = root / "deliverables"
        state_dir = root / "private-state"

        exit_code = main(
            [
                str(ROOT / "examples" / "sample-report-data.json"),
                "--out",
                str(output_dir),
                "--state-dir",
                str(state_dir),
                "--name",
                "sample",
            ]
        )

        self.assertEqual(exit_code, 0)
        self.assertTrue((state_dir / "report-data.json").is_file())
        self.assertTrue((state_dir / "sources.json").is_file())
        self.assertTrue((output_dir / "sample-working.docx").is_file())
        self.assertTrue((output_dir / "sample-clean.docx").is_file())
        self.assertFalse((output_dir / "sample-report-data.json").exists())
        self.assertFalse((output_dir / "sample-sources.json").exists())

        normalized = json.loads((state_dir / "report-data.json").read_text(encoding="utf-8"))
        self.assertIn("_calculated_progress", normalized)


if __name__ == "__main__":
    unittest.main()
