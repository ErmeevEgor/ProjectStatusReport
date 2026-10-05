from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable

STATUS_COEFFICIENTS = {
    "COMPLETED": 1.00,
    "APPROVAL": 0.90,
    "IN_PROGRESS": 0.50,
    "NOT_STARTED": 0.00,
}

# Only these four labels are allowed in the visible task/stage status column.
WORK_STATUS_LABELS = {
    "COMPLETED": "Выполнено",
    "APPROVAL": "На согласовании",
    "IN_PROGRESS": "В работе",
    "NOT_STARTED": "Не начато",
}

# Legacy aliases remain accepted so old report-data.json files do not break.
# The renderer always converts them back to one of the four canonical labels.
STATUS_ALIASES = {
    "выполнено": "COMPLETED",
    "завершено": "COMPLETED",
    "согласовано": "COMPLETED",
    "принято": "COMPLETED",
    "закрыто": "COMPLETED",
    "на согласовании": "APPROVAL",
    "на приемке": "APPROVAL",
    "на приёмке": "APPROVAL",
    "на проверке": "APPROVAL",
    "в работе": "IN_PROGRESS",
    "не начато": "NOT_STARTED",
    "факт не подтвержден": "NOT_STARTED",
    "факт не подтверждён": "NOT_STARTED",
    "требует подтверждения": "NOT_STARTED",
}

PAYMENT_EVIDENCE_LEVELS = {
    "official",
    "project_confirmed",
    "provisional",
    "missing",
}


@dataclass(frozen=True)
class ProgressResult:
    basis: str
    approved_budget: float
    budget_in_basis: float
    earned: float
    percent: float
    items: list[dict[str, Any]]


@dataclass(frozen=True)
class PaymentDisplay:
    evidence_level: str
    actual_text: str
    actual_date: str | None
    status: str


def normalize_status(status: str | None) -> str:
    if not status:
        return "NOT_STARTED"
    raw = str(status).strip()
    upper = raw.upper()
    if upper in STATUS_COEFFICIENTS:
        return upper
    low = raw.lower()
    for alias, canonical in STATUS_ALIASES.items():
        if low == alias or low.startswith(alias + " "):
            return canonical
    for alias, canonical in STATUS_ALIASES.items():
        if low.startswith(alias):
            return canonical
    raise ValueError(f"Unknown work status: {status!r}")


def display_work_status(status: str | None) -> str:
    """Return one of the four client-visible work statuses."""
    return WORK_STATUS_LABELS[normalize_status(status)]


def coefficient(status: str | None) -> float:
    return STATUS_COEFFICIENTS[normalize_status(status)]


def _costed(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        budget = item.get("budget")
        if budget is None:
            continue
        if float(budget) < 0:
            raise ValueError(f"Negative budget in item {item.get('id')}")
        result.append(item)
    return result


def _sum_budget(items: Iterable[dict[str, Any]]) -> float:
    return round(sum(float(i.get("budget") or 0) for i in items), 2)


def _baseline_kind(item: dict[str, Any], *, default: str) -> str:
    return str(item.get("baseline_kind") or default)


def is_contractual(item: dict[str, Any], *, default: str = "contract_task") -> bool:
    return _baseline_kind(item, default=default) in {"contract_task", "contract_stage"}


def _parent_id(item: dict[str, Any]) -> str | None:
    value = item.get("contract_parent_id")
    if value in (None, ""):
        value = item.get("parent_id")
    return str(value) if value not in (None, "") else None


def _lowest_complete_level(
    items: Iterable[dict[str, Any]], approved: float, tolerance: float
) -> list[dict[str, Any]] | None:
    costed = _costed(items)
    if not costed:
        return None
    ids = {str(item.get("id")) for item in costed if item.get("id") not in (None, "")}
    parents_with_costed_children = {
        parent_id for item in costed if (parent_id := _parent_id(item)) in ids
    }
    leaves = [item for item in costed if str(item.get("id")) not in parents_with_costed_children]
    if leaves and abs(_sum_budget(leaves) - approved) <= tolerance:
        return leaves
    if not parents_with_costed_children and abs(_sum_budget(costed) - approved) <= tolerance:
        return costed
    return None


def choose_progress_basis(data: dict[str, Any], tolerance: float = 1.0) -> tuple[str, list[dict[str, Any]]]:
    approved = float(data.get("approved_budget") or 0)
    if approved <= 0:
        raise ValueError("approved_budget must be positive to calculate progress")

    tasks = [
        item for item in data.get("tasks", [])
        if _baseline_kind(item, default="contract_task") == "contract_task"
    ]
    task_basis = _lowest_complete_level(tasks, approved, tolerance)
    if task_basis:
        return "tasks", task_basis

    stages = [
        item for item in data.get("tasks", [])
        if _baseline_kind(item, default="contract_task") == "contract_stage"
    ]
    stages.extend(
        item for item in data.get("stages", [])
        if _baseline_kind(item, default="contract_stage") == "contract_stage"
    )
    stage_basis = _lowest_complete_level(stages, approved, tolerance)
    if stage_basis:
        return "stages", stage_basis

    task_total = _sum_budget(_costed(tasks))
    stage_total = _sum_budget(_costed(stages))
    raise ValueError(
        "Cannot choose a complete contractual progress basis without inventing costs: "
        f"approved_budget={approved:.2f}, contractual_tasks={task_total:.2f}, "
        f"contractual_stages={stage_total:.2f}"
    )


def page2_contractual_rows(data: dict[str, Any], tolerance: float = 1.0) -> list[dict[str, Any]]:
    _, rows = choose_progress_basis(data, tolerance=tolerance)
    return rows


def inherit_parent_periods(data: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(data)
    by_id: dict[str, list[dict[str, Any]]] = {}
    for item in normalized.get("stages", []):
        item_id = item.get("id")
        if item_id not in (None, "") and is_contractual(item, default="contract_stage"):
            by_id.setdefault(str(item_id), []).append(item)
    for item in normalized.get("tasks", []):
        item_id = item.get("id")
        if item_id not in (None, "") and is_contractual(item, default="contract_task"):
            by_id.setdefault(str(item_id), []).append(item)

    for task in normalized.get("tasks", []):
        if not is_contractual(task):
            continue
        has_start = task.get("planned_start") not in (None, "")
        has_end = task.get("planned_end") not in (None, "")
        if has_start and has_end:
            task["date_basis"] = "explicit"
            continue
        parent_id = _parent_id(task)
        parents = by_id.get(parent_id or "", [])
        if len(parents) == 1:
            parent = parents[0]
            parent_start = parent.get("planned_start")
            parent_end = parent.get("planned_end")
            if parent_start not in (None, "") and parent_end not in (None, ""):
                if not has_start:
                    task["planned_start"] = parent_start
                if not has_end:
                    task["planned_end"] = parent_end
                task["date_basis"] = "parent_stage_period"
                continue
        task["date_basis"] = "missing"
    return normalized


def calculate_progress(data: dict[str, Any], tolerance: float = 1.0) -> ProgressResult:
    basis, items = choose_progress_basis(data, tolerance=tolerance)
    approved = float(data["approved_budget"])
    normalized_items: list[dict[str, Any]] = []
    earned = 0.0
    for item in items:
        budget = float(item["budget"])
        coef = coefficient(item.get("status"))
        value = round(budget * coef, 2)
        earned += value
        normalized_items.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "status": display_work_status(item.get("status")),
                "budget": budget,
                "coefficient": coef,
                "earned": value,
            }
        )
    earned = round(earned, 2)
    percent = round((earned / approved) * 100, 1) if approved else 0.0
    return ProgressResult(
        basis=basis,
        approved_budget=round(approved, 2),
        budget_in_basis=_sum_budget(items),
        earned=earned,
        percent=percent,
        items=normalized_items,
    )


def stage_progress(data: dict[str, Any], stage: dict[str, Any]) -> tuple[float, float]:
    """Return earned amount and percent for a top-level contractual stage."""
    stage_id = str(stage.get("id") or "")
    budget = float(stage.get("budget") or 0)
    progress = calculate_progress(data)
    earned = 0.0
    if progress.basis == "stages":
        for item in progress.items:
            if str(item.get("id") or "") == stage_id:
                earned = float(item.get("earned") or 0)
                break
    else:
        by_id = {str(item.get("id")): item for item in data.get("tasks", [])}
        for item in progress.items:
            raw = by_id.get(str(item.get("id") or ""), {})
            if _parent_id(raw) == stage_id:
                earned += float(item.get("earned") or 0)
    percent = round(earned / budget * 100, 1) if budget else 0.0
    return round(earned, 2), percent


def payment_plan_total(data: dict[str, Any]) -> float:
    return round(sum(float(p.get("amount") or 0) for p in data.get("payments", [])), 2)


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


def date_deviation_text(planned: Any, actual: Any) -> str:
    """Calendar-day deviation. Prefer explicit source deviation when available."""
    p = _parse_date(planned)
    a = _parse_date(actual)
    if not p or not a:
        return "—"
    delta = (a - p).days
    if delta == 0:
        return "0 дн."
    sign = "+" if delta > 0 else "−"
    return f"{sign}{abs(delta)} дн."


def payment_evidence_level(payment: dict[str, Any]) -> str:
    explicit = payment.get("fact_evidence_level")
    if explicit not in (None, ""):
        level = str(explicit)
        if level not in PAYMENT_EVIDENCE_LEVELS:
            raise ValueError(f"Unknown payment fact_evidence_level: {explicit!r}")
        return level
    status = str(payment.get("status") or "").strip().lower()
    if payment.get("requires_confirmation") is True or "требует подтверждения" in status:
        return "provisional"
    if status in {"оплачен", "оплачено", "подтвержден", "подтверждено"}:
        return "official"
    return "missing"


def resolve_payment_display(payment: dict[str, Any], report_date: Any = None) -> PaymentDisplay:
    level = payment_evidence_level(payment)
    actual_date = payment.get("actual_date") or None
    if level == "official":
        return PaymentDisplay(level, str(payment.get("actual_text") or "Факт оплаты подтвержден"), str(actual_date) if actual_date else None, "Оплачен")
    if level == "project_confirmed":
        return PaymentDisplay(level, "Факт поступления подтвержден", str(actual_date) if actual_date else None, "Подтвержден")
    if level == "provisional":
        return PaymentDisplay(level, str(payment.get("actual_text") or "Факт требует подтверждения"), str(actual_date) if actual_date else None, "Требует подтверждения")
    planned = _parse_date(payment.get("planned_date"))
    as_of = _parse_date(report_date)
    if planned is not None and as_of is not None:
        status = "Не наступил срок" if planned > as_of else "Не оплачен"
    else:
        legacy_status = str(payment.get("status") or "").strip()
        status = legacy_status if legacy_status in {"Не наступил срок", "Не оплачен"} else "Требует подтверждения"
    return PaymentDisplay(level, "—", None, status)


def progress_formula(data: dict[str, Any]) -> str:
    result = calculate_progress(data)
    if len(result.items) > 8:
        return (
            "Принцип расчета: Σ(стоимость "
            f"{len(result.items)} договорных задач × коэффициент подтвержденного статуса) "
            f"= {_format_number(result.earned)} ₽; "
            f"{_format_number(result.earned)} / {_format_number(result.approved_budget)} = "
            f"{str(f'{result.percent:.1f}').replace('.', ',')}%."
        )
    terms = [f"{_format_number(item['budget'])} × {item['coefficient'] * 100:.0f}%" for item in result.items]
    return (
        "Принцип расчета: " + " + ".join(terms)
        + f" = {_format_number(result.earned)} ₽; "
        + f"{_format_number(result.earned)} / {_format_number(result.approved_budget)} = "
        + f"{str(f'{result.percent:.1f}').replace('.', ',')}%."
    )


def _format_number(value: float) -> str:
    return f"{float(value):,.0f}".replace(",", " ")
