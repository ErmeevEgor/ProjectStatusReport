from __future__ import annotations

from copy import deepcopy


def contractual_fixture() -> dict:
    stages = [
        {
            "id": "1", "title": "Подготовка к ОПЭ", "status": "В работе", "budget": 528000,
            "planned_start": "2026-08-27", "planned_end": "2026-09-14",
            "baseline_kind": "contract_stage", "plan_source_type": "additional_agreement",
            "date_basis": "explicit", "sources": ["ds"],
        },
        {
            "id": "2", "title": "Запуск и стабилизация", "status": "Не начато", "budget": 168000,
            "planned_start": "2026-09-14", "planned_end": "2026-09-23",
            "baseline_kind": "contract_stage", "plan_source_type": "additional_agreement",
            "date_basis": "explicit", "sources": ["ds"],
        },
    ]
    specs = [
        ("1.1", "1", "Параметризация", 144000, "В работе"),
        ("1.2", "1", "НСИ", 48000, "В работе"),
        ("1.3", "1", "Инструкции", 216000, "В работе"),
        ("1.4", "1", "Обучение", 96000, "В работе"),
        ("1.5", "1", "Предпусковая проверка", 24000, "Не начато"),
        ("2.1", "2", "Запуск", 72000, "Не начато"),
        ("2.2", "2", "Стабилизация", 96000, "Не начато"),
    ]
    tasks = [
        {
            "id": task_id,
            "title": title,
            "status": status,
            "budget": budget,
            "planned_start": None,
            "planned_end": None,
            "baseline_kind": "contract_task",
            "plan_source_type": "additional_agreement",
            "contract_parent_id": parent_id,
            "contract_reference": f"Приложение №1, строка {task_id}",
            "date_basis": "missing",
            "sources": ["ds", "tracker"],
        }
        for task_id, parent_id, title, budget, status in specs
    ]
    operational = [
        {
            "id": f"OP-{number:02d}",
            "title": f"Внутренняя задача {number}",
            "status": "В работе",
            "budget": 34800,
            "baseline_kind": "operational",
            "plan_source_type": "other",
            "sources": ["tracker"],
        }
        for number in range(1, 21)
    ]
    return {
        "report": {
            "customer": "Заказчик", "project_name": "Проект", "report_number": 2,
            "report_date": "2026-09-21", "reporting_period": "15.09.2026–21.09.2026",
            "stage_name": "ОПЭ", "overall_status_points": ["Работы продолжаются."] * 4,
        },
        "approved_budget": 696000,
        "stages": stages,
        "tasks": tasks,
        "operational_items": operational,
        "payments": [],
        "risks": [],
        "health_check": [
            {"number": 2, "question": "Есть отклонение от плановых сроков?", "answer": "Нет", "sources": []},
            {"number": 7, "question": "Есть открытые риски проекта?", "answer": "Нет", "sources": []},
        ],
        "open_items": [],
        "sources": [
            {"id": "ds", "type": "additional_agreement", "name": "ДС", "confidence": "confirmed"},
            {"id": "tracker", "type": "task_tracker", "name": "Tracker", "confidence": "confirmed"},
        ],
    }


def valid_covered_fixture() -> dict:
    data = deepcopy(contractual_fixture())
    data["risks"] = [
        {
            "id": "R1", "date": "2026-09-21", "type": "ОТКЛОНЕНИЕ",
            "title": "Нарушен договорный график подготовки к запуску",
            "probability_or_fact": "Факт", "impact_degree": "Высокая",
            "impact": "Задерживается готовность к запуску.",
            "actions": "Согласовать корректирующий график.", "result": None,
            "status": "Открыт", "related_task_ids": ["1.1", "1.2", "1.3", "1.4", "1.5"],
            "related_open_item_ids": [], "materiality": "high", "sources": ["tracker"],
        }
    ]
    data["health_check"][0]["answer"] = "Да"
    data["health_check"][1]["answer"] = "Да"
    return data
