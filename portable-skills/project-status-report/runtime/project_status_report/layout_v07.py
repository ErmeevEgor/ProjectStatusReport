from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Any

from . import render_docx as _core

_PAGE2_OLD_HEADERS = [
    "№",
    "Задача / результат",
    "Ответственный",
    "Статус",
    "Бюджет",
    "Расчетное освоение",
    "Плановое начало",
    "Плановое завершение",
    "Фактическое завершение",
    "Комментарий",
]

_PAGE2_NEW_HEADERS = [
    "Код задачи",
    "Наименование",
    "Задача",
    "Статус",
    "Бюджет",
    "Освоено",
    "План начала",
    "План завершения",
    "Факт",
    "Комментарий",
]

_RENDER_LOCK = Lock()


def _stable_page2_rows(data: dict[str, Any], original_page2_rows):
    """Map whichever contractual rows v0.6 selects into the v0.7 columns.

    The contractual baseline can come from tasks[] or directly from stages[].
    Core v0.6 renders column 2 from title/result and column 3 from owner.  For
    the v0.7 fallback we deliberately reuse those slots as:
      column 2 -> Наименование (title)
      column 3 -> Задача (result)
    without changing status, budget, dates, progress or source traceability.
    """
    rows = original_page2_rows(data)
    stable_rows: list[dict[str, Any]] = []
    for item in rows:
        row = deepcopy(item)
        row["owner"] = row.get("result")
        row["result"] = None
        stable_rows.append(row)
    return stable_rows


def render_report(
    data: dict[str, Any],
    out_path: str | Path,
    *,
    include_comments: bool = True,
) -> Path:
    """Render v0.7 fallback layout with a stable task table.

    Previous-OSP layout inheritance is orchestrated by SKILL.md. This renderer is
    the fallback used when no previous DOCX structure is available.
    """
    with _RENDER_LOCK:
        original_header_row = _core._header_row
        original_page2_rows = _core.page2_contractual_rows

        def _header_row(doc, row, labels, size=5.7):
            if labels == _PAGE2_OLD_HEADERS:
                labels = _PAGE2_NEW_HEADERS
            return original_header_row(doc, row, labels, size)

        def _page2_contractual_rows(data):
            return _stable_page2_rows(data, original_page2_rows)

        _core._header_row = _header_row
        _core.page2_contractual_rows = _page2_contractual_rows
        try:
            return _core.render_report(
                data,
                out_path,
                include_comments=include_comments,
            )
        finally:
            _core._header_row = original_header_row
            _core.page2_contractual_rows = original_page2_rows
