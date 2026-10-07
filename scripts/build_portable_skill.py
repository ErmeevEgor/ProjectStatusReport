#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "portable-skills" / "project-status-report"
RELEASE = ROOT / "release"

# v0.9.0 canonical portable skill is documentation/schema/reference based.
# Legacy runtime/wrapper scripts may remain in the repository temporarily,
# but must not be packaged into the portable release.
EXCLUDED_TOP_LEVEL = {"runtime", "scripts"}


def should_package(path: Path) -> bool:
    relative = path.relative_to(SKILL)
    if not relative.parts:
        return False
    return relative.parts[0] not in EXCLUDED_TOP_LEVEL


def make_zip() -> tuple[Path, Path]:
    meta = json.loads((SKILL / "release.json").read_text(encoding="utf-8"))
    RELEASE.mkdir(parents=True, exist_ok=True)

    archive = RELEASE / f"{meta['name']}-{meta['version']}.zip"
    if archive.exists():
        archive.unlink()

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        files = sorted(p for p in SKILL.rglob("*") if p.is_file() and should_package(p))
        for file in files:
            zf.write(file, file.relative_to(SKILL.parent).as_posix())

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    return archive, checksum


def main() -> int:
    archive, checksum = make_zip()
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
