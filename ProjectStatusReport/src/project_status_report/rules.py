from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

STATUS_COEFFICIENTS = {
    "COMPLETED": 1.00,
    "APPROVAL": 0.90,
    "IN_PROGRESS": 0.50,
    "NOT_STARTED": 0.00,
}

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
}


@dataclass(frozen=True)
class ProgressResult:
    basis: str
    approved_budget: float
    budget_in_basis: float
    earned: float
    percent: float
    items: list[dict[str, Any]]


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


def choose_progress_basis(data: dict[str, Any], tolerance: float = 1.0) -> tuple[str, list[dict[str, Any]]]:
    approved = float(data.get("approved_budget") or 0)
    if approved <= 0:
        raise ValueError("approved_budget must be positive to calculate progress")

    tasks = _costed(data.get("tasks", []))
    stages = _costed(data.get("stages", []))

    if tasks and abs(_sum_budget(tasks) - approved) <= tolerance:
        return "tasks", tasks
    if stages and abs(_sum_budget(stages) - approved) <= tolerance:
        return "stages", stages

    task_total = _sum_budget(tasks)
    stage_total = _sum_budget(stages)
    raise ValueError(
        "Cannot choose progress basis without inventing costs: "
        f"approved_budget={approved:.2f}, costed_tasks={task_total:.2f}, costed_stages={stage_total:.2f}"
    )


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
                "status": item.get("status"),
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


def payment_plan_total(data: dict[str, Any]) -> float:
    return round(sum(float(p.get("amount") or 0) for p in data.get("payments", [])), 2)
