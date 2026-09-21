#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "portable-skills" / "project-status-report"
SOURCE = ROOT / "src" / "project_status_report"
RUNTIME = SKILL / "runtime" / "project_status_report"
RELEASE = ROOT / "release"


def sync_runtime() -> None:
    if RUNTIME.exists():
        shutil.rmtree(RUNTIME)
    RUNTIME.mkdir(parents=True)
    for source in SOURCE.rglob("*.py"):
        target = RUNTIME / source.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def sync_scripts() -> None:
    scripts = SKILL / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    wrapper = """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "runtime"))

from project_status_report.cli import main

raise SystemExit(main())
"""
    (scripts / "generate_report.py").write_text(wrapper, encoding="utf-8")


def make_zip() -> tuple[Path, Path]:
    meta = json.loads((SKILL / "release.json").read_text(encoding="utf-8"))
    RELEASE.mkdir(parents=True, exist_ok=True)
    archive = RELEASE / f"{meta['name']}-{meta['version']}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in sorted(p for p in SKILL.rglob("*") if p.is_file()):
            zf.write(file, file.relative_to(SKILL.parent).as_posix())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    return archive, checksum


def main() -> int:
    sync_runtime()
    sync_scripts()
    archive, checksum = make_zip()
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
