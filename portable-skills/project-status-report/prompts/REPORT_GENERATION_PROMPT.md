# Internal LLM prompt — Project Status Report v0.7

Build normalized `report-data.json` from project evidence. Preserve source traceability and use deterministic rules for calculations and validation.

## Previous-first continuity

If a previous ОСП exists, use it for both factual continuity and document structure.

Before designing any layout:
1. inspect the previous ОСП;
2. capture page/section order;
3. capture table names, columns, order and grouping;
4. reuse that compatible structure in the new report;
5. update facts/statuses without redesigning recurring tables.

If no previous ОСП exists, use the built-in fallback structure from `references/report-structure.md`.

For `Данные по задачам`, keep the previous task-table structure. For fallback use:
`Код задачи | Наименование | Задача | Статус | Бюджет | Освоено | План начала | План завершения | Факт | Комментарий`.

Never substitute a row number for the task code. Never collapse `Наименование` and `Задача` when both are available. `План начала` and `План завершения` are separate fields.

## Continuity data

Increment the previous report number. Normally set `report.reporting_period` from the previous report date through current `report.report_date`. Do not invent dates. Carry forward unresolved risks/open items and reconcile them against new evidence.

## Project passport

Extract customer, project name, project managers, contract basis, all applicable DS, report number/period, project start date, current stage.

## Multiple additional agreements / stages

Create `stages[]` with one row per active contractual stage/DS. Old closed stages are excluded from the active calculation baseline unless needed as historical context.

## Work statuses

Every stage/task/operational item visible status is exactly one of:
- Не начато
- В работе
- На согласовании
- Выполнено

Payment statuses remain separate.

## Progress

Use contractual budget weighting 0 / 50 / 90 / 100%. Operational items never participate. Use the lowest explicit costing level covering the approved budget without parent/child double count.

## Page 1 management data

Write concise management status points consistent with schedule, payments, risks and stage table.

## Risks and control questions

Use `РИСК` / `ПРОБЛЕМА` / `ОТКЛОНЕНИЕ`. Visible heading: `Контроль состояния проекта`.

## Output discipline

Do not put service/source wording into client-visible text. Missing facts remain null/blank rather than guessed. Every material fact carries source IDs.

## Incremental state

If external `report-data.json`, `sources.json`, `source-manifest.json` exist, reuse unchanged facts and process only changed evidence. Previous clean DOCX remains the structural baseline for the next report.
