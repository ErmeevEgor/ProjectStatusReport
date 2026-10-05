# Internal LLM prompt — Project Status Report v0.6

Build normalized `report-data.json` from project evidence; deterministic runtime renders DOCX.

## Continuity

If a previous ОСП exists, increment its number and normally set `report.reporting_period` from the previous report date through the current `report.report_date`. If the previous date cannot be established, do not invent it.

## Project passport

Extract:
- `customer`;
- `project_name`;
- `contractor_pm`;
- `customer_pm`;
- `contract_basis` = main contract only;
- `additional_agreements` = all applicable DS references in current scope; legacy `additional_agreement` may also be populated;
- `report_number`;
- `reporting_period`;
- `project_start_date` = start of the project itself, not the current stage;
- `stage_name`.

Project start date priority: explicit project/contract record → previous approved ОСП → official project document/minutes → reliable project correspondence. Do not substitute current DS start automatically.

## Multiple additional agreements / stages

Create top-level `stages[]` with one row per active contractual stage/DS included in the report scope. Fill `contract_reference` with the DS reference and extract:
- planned_start;
- actual_start if fact is supported;
- start_deviation if explicitly known;
- planned_end;
- actual_end if fact is supported;
- end_deviation if explicitly known;
- budget;
- status;
- sources.

## Work statuses

Every `stages[]`, `tasks[]`, and `operational_items[]` status must be exactly:
- Не начато
- В работе
- На согласовании
- Выполнено

Never generate `Факт не подтвержден` or `Требует подтверждения` as a work status.

Lifecycle rule:
- no supported start → Не начато;
- supported start/work → В работе;
- result submitted for approval/acceptance → На согласовании;
- result completed/agreed/accepted → Выполнено.

If completion is uncertain, keep the lifecycle status and place the uncertainty in `comment` / `requires_confirmation`; do not invent a fifth status.

## Progress

Use contractual budget weighting 0 / 50 / 90 / 100%. Operational items never participate. Use the lowest explicit costing level covering the approved budget without parent/child double count.

## Page 1 management data

Write 4–6 `overall_status_points`. Ensure they are consistent with plan/fact schedule, payments, risks, and the stage table.

## Risks and control questions

Keep existing risk coverage and state consistency rules. The visible heading for `health_check` is `Контроль состояния проекта`.

## Output discipline

Do not put source/service wording into visible report text. Every material fact should carry source IDs. Missing facts remain null/blank rather than guessed.

## Payments

Preserve the existing payment evidence model. Do not map payment statuses through work statuses. Never invent payment dates.

## Risk coverage and consistency

Review overdue contractual work, blockers, high/medium open items and unresolved prior risks. Use `РИСК` / `ПРОБЛЕМА` / `ОТКЛОНЕНИЕ` appropriately. Before output, ensure schedule, risk, payment and control-question states do not contradict each other.

## Incremental state

If an external prior `report-data.json` / `sources.json` / source manifest exists, reuse unchanged normalized facts and process only changed evidence. Do not silently drop unresolved prior items.
