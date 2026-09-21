from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .rules import calculate_progress, payment_plan_total


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_report(data: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    required_top = [
        "report", "approved_budget", "stages", "tasks",
        "payments", "risks", "health_check", "open_items", "sources",
    ]
    for key in required_top:
        if key not in data:
            errors.append(f"Missing top-level field: {key}")

    report = data.get("report") or {}
    for key in ["customer", "project_name", "report_number", "report_date", "reporting_period", "stage_name"]:
        if key not in report:
            errors.append(f"Missing report field: {key}")

    points = report.get("overall_status_points") or []
    if not 4 <= len(points) <= 6:
        warnings.append(f"overall_status_points should usually contain 4-6 management points; got {len(points)}")

    source_ids = {s.get("id") for s in data.get("sources", []) if s.get("id")}
    for collection in ["stages", "tasks", "payments", "risks", "health_check", "open_items"]:
        for idx, item in enumerate(data.get(collection, [])):
            for source_id in item.get("sources", []) or []:
                if source_id not in source_ids:
                    errors.append(f"{collection}[{idx}] references unknown source {source_id!r}")

    for field, ids in (report.get("field_sources") or {}).items():
        for source_id in ids:
            if source_id not in source_ids:
                errors.append(f"report.field_sources[{field!r}] references unknown source {source_id!r}")

    approved = float(data.get("approved_budget") or 0)
    if approved <= 0:
        errors.append("approved_budget must be greater than zero")
    else:
        try:
            progress = calculate_progress(data)
            if abs(progress.budget_in_basis - approved) > 1.0:
                errors.append("Progress costing basis does not sum to approved_budget")
        except ValueError as exc:
            errors.append(str(exc))

    payment_total = payment_plan_total(data)
    if approved > 0 and data.get("payments") and abs(payment_total - approved) > 1.0:
        warnings.append(
            "Payment plan total differs from approved budget. Verify contract/DS terms. "
            f"payments={payment_total:.2f}, approved_budget={approved:.2f}"
        )

    open_risks = [
        r for r in data.get("risks", [])
        if str(r.get("status", "")).strip().lower() not in {"закрыт", "закрыто", "выполнено"}
    ]
    q7 = next((h for h in data.get("health_check", []) if int(h.get("number") or 0) == 7), None)
    if q7:
        answer = str(q7.get("answer", "")).strip().lower()
        should_yes = bool(open_risks)
        if should_yes and answer not in {"да", "есть", "да, есть"}:
            errors.append("Health check #7 contradicts open risks on page 3: expected 'Да'")
        if not should_yes and answer in {"да", "есть", "да, есть"}:
            errors.append("Health check #7 contradicts page 3: no open risks, expected 'Нет'")

    forbidden = ("по контексту проекта", "по памяти llm", "найдено в чате", "нужно проверить вручную")

    def scan(value: Any, path: str) -> None:
        if isinstance(value, str):
            low = value.lower()
            for phrase in forbidden:
                if phrase in low:
                    warnings.append(f"Service phrase in visible data at {path}: {phrase!r}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                scan(v, f"{path}[{i}]")
        elif isinstance(value, dict):
            for k, v in value.items():
                if k not in {"note", "reference"}:
                    scan(v, f"{path}.{k}")

    scan(data.get("report", {}), "report")
    for name in ["stages", "tasks", "payments", "risks", "health_check", "open_items"]:
        scan(data.get(name, []), name)

    return ValidationResult(errors=errors, warnings=warnings)
