from __future__ import annotations

import unittest
from pathlib import Path

from project_status_report.state import compare_sources


ROOT = Path(__file__).resolve().parents[1]


class SourceManifestTests(unittest.TestCase):
    def test_unchanged_and_changed_sources_are_separated(self):
        directory = ROOT / "output" / "test-artifacts" / "source-manifest"
        directory.mkdir(parents=True, exist_ok=True)
        source = directory / "chat.zip"
        source.write_bytes(b"one")
        first = compare_sources([source], {"version": 1, "sources": []})
        second = compare_sources(
            [source], {"version": 1, "sources": first["sources"]}
        )
        self.assertEqual(len(second["delta"]["unchanged"]), 1)
        source.write_bytes(b"two")
        third = compare_sources(
            [source], {"version": 1, "sources": first["sources"]}
        )
        self.assertEqual(len(third["delta"]["changed"]), 1)


if __name__ == "__main__":
    unittest.main()
