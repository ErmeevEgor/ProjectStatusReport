from __future__ import annotations

import os
import unittest
from pathlib import Path

from project_status_report.confluence import (
    ConfluenceClient,
    docx_to_confluence_storage,
    latest_report_page,
    load_local_config,
    save_local_config,
)


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

    def test_update_page_increments_version_and_preserves_title(self):
        calls = []

        class RecordingClient(ConfluenceClient):
            def _request(self, method, path, **kwargs):
                calls.append((method, path, kwargs))
                if method == "GET":
                    return {"id": "42", "title": "ОСП 3", "version": {"number": 7}}
                return {"id": "42", "title": kwargs["payload"]["title"]}

        client = RecordingClient("https://example.test", "secret", user="user")
        page = client.update_page("42", "<h1>Report</h1>")
        self.assertEqual(page["title"], "ОСП 3")
        method, path, kwargs = calls[-1]
        self.assertEqual((method, path), ("PUT", "/rest/api/content/42"))
        self.assertEqual(kwargs["payload"]["version"]["number"], 8)
        self.assertEqual(
            kwargs["payload"]["body"]["storage"]["value"], "<h1>Report</h1>"
        )

    @unittest.skipUnless(os.name == "nt", "Windows DPAPI test")
    def test_local_config_encrypts_and_round_trips_token(self):
        directory = ROOT / "output" / "test-artifacts" / "confluence-config"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "confluence.local.json"
        save_local_config(
            path,
            base_url="https://example.test/",
            user="EVErmeev",
            auth_mode="basic",
            token="test-secret",
        )
        raw = path.read_text(encoding="utf-8")
        self.assertNotIn("test-secret", raw)
        loaded = load_local_config(path)
        self.assertEqual(loaded["token"], "test-secret")
        self.assertEqual(loaded["base_url"], "https://example.test")


if __name__ == "__main__":
    unittest.main()
