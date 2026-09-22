from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .render_docx import render_report
from .rules import calculate_progress, inherit_parent_periods, page2_contractual_rows
from .validation import validate_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a four-page Project Status Report (ОСП).")
    parser.add_argument("input", type=Path, help="report-data.json")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory")
    parser.add_argument("--name", default="project-status", help="Output basename")
    args = parser.parse_args(argv)

    data = inherit_parent_periods(json.loads(args.input.read_text(encoding="utf-8")))
    validation = validate_report(data)

    for warning in validation.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if validation.errors:
        for error in validation.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    progress = calculate_progress(data)
    normalized = dict(data)
    normalized["_calculated_progress"] = {
        "basis": progress.basis,
        "approved_budget": progress.approved_budget,
        "earned": progress.earned,
        "percent": progress.percent,
        "items": progress.items,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    normalized_path = args.out / f"{args.name}-report-data.json"
    normalized_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sources_path = args.out / f"{args.name}-sources.json"
    derived_facts = [
        {
            "field": f"tasks[{item.get('id')}].planned_period",
            "basis": "parent_stage_period",
            "contract_parent_id": item.get("contract_parent_id") or item.get("parent_id"),
            "planned_start": item.get("planned_start"),
            "planned_end": item.get("planned_end"),
            "source_ids": item.get("sources", []),
        }
        for item in page2_contractual_rows(data)
        if item.get("date_basis") == "parent_stage_period"
    ]
    sources_output = {"sources": data.get("sources", []), "derived_facts": derived_facts}
    sources_path.write_text(json.dumps(sources_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    render_report(data, args.out / f"{args.name}-working.docx", include_comments=True)
    render_report(data, args.out / f"{args.name}-clean.docx", include_comments=False)

    print(f"Progress: {progress.percent:.1f}% ({progress.earned:.2f}/{progress.approved_budget:.2f})")
    print(f"Created: {args.out / f'{args.name}-working.docx'}")
    print(f"Created: {args.out / f'{args.name}-clean.docx'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
