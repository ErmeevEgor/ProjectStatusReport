from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def fingerprint(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    digest = hashlib.sha256()
    with resolved.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    stat = resolved.stat()
    return {
        "path": str(resolved),
        "name": resolved.name,
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": digest.hexdigest(),
    }


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "sources": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("version") or 0) != 1:
        raise ValueError("Unsupported source manifest version")
    return payload


def compare_sources(paths: Iterable[Path], previous: dict[str, Any]) -> dict[str, Any]:
    current = [fingerprint(path) for path in paths]
    previous_by_path = {
        str(item.get("path")): item for item in previous.get("sources", [])
    }
    current_paths = {item["path"] for item in current}
    added: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    unchanged: list[dict[str, Any]] = []
    for item in current:
        before = previous_by_path.get(item["path"])
        if before is None:
            added.append(item)
        elif before.get("sha256") != item["sha256"]:
            changed.append(item)
        else:
            unchanged.append(item)
    missing = [
        item
        for item in previous.get("sources", [])
        if str(item.get("path")) not in current_paths
    ]
    return {
        "version": 1,
        "sources": current,
        "delta": {
            "added": added,
            "changed": changed,
            "unchanged": unchanged,
            "missing": missing,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare source file hashes before re-reading project evidence."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("sources", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for source in args.sources:
        if not source.is_file():
            parser.error(f"Source is not a file: {source}")
    result = compare_sources(args.sources, load_manifest(args.manifest))
    if args.write:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        stored = {"version": 1, "sources": result["sources"]}
        args.manifest.write_text(
            json.dumps(stored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(result["delta"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
