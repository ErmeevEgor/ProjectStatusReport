from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .rules import (
    calculate_progress,
    inherit_parent_periods,
    normalize_status,
    page2_contractual_rows,
    payment_plan_total,
)


@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_closed(status: Any) -> bool:
    return str(status or "").strip().lower() in {
        "закрыт", "закрыта", "закрыто", "выполнено", "завершено", "согласовано", "принято"
    }


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def _yes(value: Any) -> bool:
    return str(value or "").strip().lower() in {"да", "есть", "да, есть"}


def validate_report(data: dict[str, Any]) -> ValidationResult:
    data = inherit_parent_periods(data)
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
    for collection in [
        "stages", "tasks", "operational_items", "payments", "risks", "health_check",
        "open_items", "previous_risks", "risk_reconciliation",
    ]:
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

    source_by_id = {s.get("id"): s for s in data.get("sources", []) if s.get("id")}
    for task in data.get("tasks", []):
        task_id = task.get("id", "?")
        if task.get("baseline_kind") == "operational":
            errors.append(f"Page 2 task {task_id!r} has baseline_kind=operational and cannot be rendered or costed")
    try:
        page2_rows = page2_contractual_rows(data)
    except ValueError:
        page2_rows = [task for task in data.get("tasks", []) if task.get("baseline_kind") != "operational"]
    for task in page2_rows:
        task_id = task.get("id", "?")
        source_types = {
            str(source_by_id[sid].get("type") or "").strip().lower()
            for sid in task.get("sources", []) or []
            if sid in source_by_id
        }
        explicit_type = str(task.get("plan_source_type") or "").strip().lower()
        contractual = explicit_type in {"contract", "additional_agreement"} or bool(
            source_types & {"contract", "additional_agreement"}
        )
        if not contractual:
            errors.append(
                f"Page 2 task is not supported by contractual baseline. task_id={task_id!r}"
            )

    payment_total = payment_plan_total(data)
    if approved > 0 and data.get("payments") and abs(payment_total - approved) > 1.0:
        warnings.append(
            "Payment plan total differs from approved budget. Verify contract/DS terms. "
            f"payments={payment_total:.2f}, approved_budget={approved:.2f}"
        )

    open_risks = [r for r in data.get("risks", []) if not _is_closed(r.get("status"))]
    risk_task_ids = {
        str(task_id)
        for risk in open_risks
        for task_id in (risk.get("related_task_ids") or [])
    }
    risk_open_item_ids = {
        str(item_id)
        for risk in open_risks
        for item_id in (risk.get("related_open_item_ids") or [])
    }

    report_date = _parse_date(report.get("report_date"))
    if report.get("report_date") and report_date is None:
        warnings.append(f"Cannot parse report.report_date for overdue coverage: {report.get('report_date')!r}")
    if report_date:
        try:
            contractual_rows = page2_contractual_rows(data)
        except ValueError:
            contractual_rows = [
                task for task in data.get("tasks", []) if task.get("baseline_kind") != "operational"
            ]
        for task in contractual_rows:
            planned_end = _parse_date(task.get("planned_end"))
            try:
                completed = normalize_status(task.get("status")) == "COMPLETED"
            except ValueError:
                completed = False
            if planned_end and planned_end < report_date and not completed:
                task_id = str(task.get("id") or "")
                excluded = str(task.get("risk_impact") or "").strip().lower() == "none"
                has_reason = bool(str(task.get("risk_impact_reason") or "").strip())
                if task_id not in risk_task_ids and not (excluded and has_reason):
                    errors.append(
                        "Overdue incomplete contractual task requires risk coverage or "
                        f"risk_impact=none with explanation. task_id={task_id!r}"
                    )

    for item in data.get("open_items", []):
        if str(item.get("priority") or "").lower() in {"high", "medium"} and not _is_closed(item.get("status")):
            item_id = str(item.get("id") or "")
            if not item_id:
                errors.append("Material open item requires a non-empty id for risk coverage")
                continue
            excluded = str(item.get("risk_impact") or "").strip().lower() == "none"
            has_reason = bool(str(item.get("risk_impact_reason") or "").strip())
            if item_id not in risk_open_item_ids and not (excluded and has_reason):
                errors.append(f"Material open item requires risk coverage. open_item_id={item_id!r}")

    previous_open_ids = {
        str(risk.get("id"))
        for risk in data.get("previous_risks", [])
        if risk.get("id") not in (None, "") and not _is_closed(risk.get("status"))
    }
    reconciled_ids = {
        str(item.get("previous_risk_id"))
        for item in data.get("risk_reconciliation", [])
        if item.get("result") in {"carried_forward", "closed", "transformed", "not_applicable"}
    }
    for risk_id in sorted(previous_open_ids - reconciled_ids):
        errors.append(f"Previous open risk has no reconciliation result. previous_risk_id={risk_id!r}")
    current_risk_ids = {str(risk.get("id")) for risk in data.get("risks", []) if risk.get("id")}
    for item in data.get("risk_reconciliation", []):
        result = item.get("result")
        current_id = str(item.get("current_risk_id") or "")
        if result in {"carried_forward", "transformed"} and current_id not in current_risk_ids:
            errors.append(
                "Risk reconciliation result requires a valid current_risk_id. "
                f"previous_risk_id={item.get('previous_risk_id')!r}"
            )
        if result in {"closed", "not_applicable"}:
            if not str(item.get("reason") or "").strip() or not item.get("sources"):
                errors.append(
                    "Closed/not-applicable previous risk requires a reason and source. "
                    f"previous_risk_id={item.get('previous_risk_id')!r}"
                )

    for risk in data.get("risks", []):
        if risk.get("type") == "ПРОБЛЕМА" and risk.get("probability_or_fact") not in {None, "", "—", "Реализовано"}:
            errors.append(f"Realized problem must not have probability. risk_id={risk.get('id')!r}")
        if risk.get("type") == "ОТКЛОНЕНИЕ" and risk.get("probability_or_fact") != "Факт":
            errors.append(f"Deviation must use probability_or_fact='Факт'. risk_id={risk.get('id')!r}")

    q7 = next((h for h in data.get("health_check", []) if int(h.get("number") or 0) == 7), None)
    if q7:
        should_yes = bool(open_risks)
        if should_yes and not _yes(q7.get("answer")):
            errors.append("Health check #7 contradicts open risks on page 3: expected 'Да'")
        if not should_yes and _yes(q7.get("answer")):
            errors.append("Health check #7 contradicts page 3: no open risks, expected 'Нет'")

    open_schedule_deviation = any(
        risk.get("type") == "ОТКЛОНЕНИЕ"
        and not _is_closed(risk.get("status"))
        and any(word in " ".join(str(risk.get(k) or "") for k in ("title", "impact")).lower()
                for word in ("срок", "график", "просроч"))
        for risk in data.get("risks", [])
    )
    q2 = next((h for h in data.get("health_check", []) if int(h.get("number") or 0) == 2), None)
    if q2 and open_schedule_deviation and not _yes(q2.get("answer")):
        errors.append("Health check #2 contradicts an open schedule deviation: expected 'Да'")

    normalized_open_texts = {
        " ".join(str(item.get("item") or "").lower().split()) for item in data.get("open_items", [])
    }
    for risk in data.get("risks", []):
        risk_text = " ".join(str(risk.get("title") or "").lower().split())
        if risk_text and risk_text in normalized_open_texts:
            errors.append("Page 3 risk and page 4 open item must describe impact and action differently")

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
    for name in [
        "stages", "tasks", "operational_items", "payments", "risks", "health_check",
        "open_items", "previous_risks", "risk_reconciliation",
    ]:
        scan(data.get(name, []), name)

    return ValidationResult(errors=errors, warnings=warnings)
