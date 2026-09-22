from __future__ import annotations

from copy import deepcopy
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


def _baseline_kind(item: dict[str, Any], *, default: str) -> str:
    """Return a baseline kind while retaining compatibility with v0.1 data."""
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
    """Choose a complete costed level without counting a parent with its children."""
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

    # A flat contractual list (or a parent-only list) is a valid complete level.
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

    # Contractual stages can be provided in the page-2 task array or in the
    # legacy top-level stages array. Operational rows are always excluded.
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
    """Return exactly the contractual rows that belong on page 2."""
    _, rows = choose_progress_basis(data, tolerance=tolerance)
    return rows


def inherit_parent_periods(data: dict[str, Any]) -> dict[str, Any]:
    """Fill missing child dates only when a contractual parent is unambiguous."""
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
