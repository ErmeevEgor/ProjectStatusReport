---
name: project-status-report
description: Build a four-page project status report (ОСП) from project evidence, with contractual plan/fact, weighted budget progress, risks, payments and Confluence-safe DOCX output.
---

# Project Status Report

Create/update an ОСП from project context, exported chats, contract, all applicable additional agreements, acts/UPD, payment evidence, prior ОСП and operational project documents. Never invent unsupported facts.

## Continuity and layout inheritance

A previous ОСП is not only a factual continuity source; it is the primary structural template for the next report.

- If a previous ОСП exists, use it for report number, previous report date, unresolved risks/questions/tasks and continuity.
- If a previous clean DOCX is available, make a copy and update that copy in place. Preserve its page/section order, section names, table names, table column set and order, grouping, column meaning, widths and general visual hierarchy. Do not redesign a recurring ОСП without an explicit user request or a hard incompatibility with the current skill rules.
- If the previous ОСП is available only as PDF, use it as the structural reference and reproduce the same section/table structure in the new DOCX as closely as possible.
- For the recurring `Данные по задачам` block, reuse the previous task-table structure. Keep existing contractual rows for the same scope and update their statuses/facts; add or remove contractual rows only when the applicable contract/DS actually changes the scope.
- `План начала` and `План завершения` are separate semantic fields and must be separate visible columns whenever the previous table had them separately or the built-in fallback template is used.
- Do not replace task names with row numbers or internal IDs. A code/ID column, when present, is separate from the human-readable task name.
- `reporting_period` is normally the period from the previous ОСП date to the current `report_date`.
- If that period cannot be established reliably, keep the field but do not invent dates.
- If the user explicitly says there was no prior ОСП, create report №1.

### Structural precedence

Use this precedence for document layout:
1. previous clean ОСП supplied for the same project;
2. previous ОСП in another readable format for the same project;
3. built-in fallback structure from `references/report-structure.md` and the packaged renderer.

Current hard requirements still apply to inherited layouts: exactly four visible work statuses, contractual progress without double counting, separate payment statuses, source traceability, Confluence-safe clean DOCX, and exactly four pages. When an inherited layout conflicts with a hard requirement, preserve as much of the previous layout as possible and change only the conflicting element.

## Source priority

For contractual plan: signed contract → signed additional agreements → later equal-force official documents.
For fact: acts/UPD/acceptance → official operational systems/docs → approved minutes → project correspondence.
A later factual source cannot silently overwrite the contractual baseline.

## Page 1 — mandatory data semantics

When there is no previous ОСП, use the built-in fallback layout below. When a previous ОСП exists, preserve its compatible structure while ensuring all mandatory data is present.

### Passport

Use a vertical two-column table in the fallback template. One entity = one row. Never put `Заказчик` and `Проект` in parallel columns.

Rows, in this order in the fallback template:
1. Заказчик
2. Проект
3. Руководитель проекта от Исполнителя
4. Руководитель проекта от Заказчика
5. Основание
6. Номер отчета
7. Отчетный период

`Основание` must contain the main contract plus every applicable additional agreement. Use `report.contract_basis`, `report.additional_agreements[]`, and legacy `report.additional_agreement` as fallback.

### Сводные данные по проекту

Show:
- `report.project_start_date` — date the project itself started, not the start of the current DS/stage;
- `report.stage_name` — current project stage/scope;
- approved budget of the active report scope;
- earned budget and total progress percent.

Do not substitute the start date of the newest DS for `project_start_date`.

### План и статус этапов / дополнительных соглашений

Use top-level `stages[]` to summarize each active contractual stage/DS. For multi-DS projects there must be one row per active contractual stage/DS.

Fallback columns:
- Этап / ДС
- План начала
- Факт начала
- Отклонение начала
- План завершения
- Факт завершения
- Отклонение завершения
- Статус
- Бюджет
- Освоено / %

Populate `contract_reference` with the DS/contract reference for each stage where available. Use `actual_start`, `actual_end`, `start_deviation`, `end_deviation` when evidence exists. If explicit deviation is absent, runtime may display a calendar-day delta from plan/fact dates. Never invent an actual date.

### Work status model — exactly four visible statuses

For stages, contractual tasks and operational items the visible status must be exactly one of:
- `Не начато` = 0%
- `В работе` = 50%
- `На согласовании` = 90%
- `Выполнено` = 100%

Do not output `Факт не подтвержден`, `Требует подтверждения`, `На проверке`, `На приемке`, etc. as visible work statuses. Legacy input values may be accepted internally, but renderer normalizes them to the four labels.

When evidence is insufficient, determine the lifecycle state conservatively:
- no evidence of start → `Не начато`;
- evidence that work on the item started → `В работе`;
- result submitted for approval/acceptance → `На согласовании`;
- result completed/agreed/accepted → `Выполнено`.
Use `requires_confirmation` or comments for uncertainty; do not create a fifth status.

### Общий статус проекта

4–6 concise management bullets: current scope, achieved result, next focus, schedule, budget/progress/payment state, key dependency/risk.

### План / факт оплат

Keep the existing payment evidence model (`official`, `project_confirmed`, `provisional`, `missing`). Payment statuses are separate from work statuses.

## Page 2 — Данные по задачам

If a previous ОСП exists, inherit this table from it rather than inventing a new table design.

For the built-in fallback template use exactly these contractual columns, in this order:
1. `Код задачи`
2. `Наименование`
3. `Задача`
4. `Статус`
5. `Бюджет`
6. `Освоено`
7. `План начала`
8. `План завершения`
9. `Факт`
10. `Комментарий`

`Код задачи` is the contractual/task code. `Наименование` is the human-readable requirement/work name. `Задача` is the contractual subtask/result such as preparation/agreement or implementation/delivery. Never collapse `Наименование` and `Задача` into a single technical label when both are available.

Use the lowest explicitly costed contractual level covering the approved budget without double counting parent + child. Operational items are shown separately and never participate in progress.

All visible work statuses are normalized to the four-status model above.

## Page 3 — Риски проекта

Use `РИСК`, `ПРОБЛЕМА`, `ОТКЛОНЕНИЕ`. Keep `Ключевой вывод по рискам` and optional `Финансовое наблюдение` as normal paragraphs, not decorative table cells.

## Page 4 — Ключевые вопросы и проблемы

The subsection previously called `Health check` must be titled:

`Контроль состояния проекта`

Keep the seven control questions and consistency checks. Then show `Открытые вопросы / действия` and `Следующий контрольный ориентир`.

## Progress

Progress is weighted by budget, not task count. Coefficients are fixed at 0 / 0.5 / 0.9 / 1.0. Do not double count parents and children. Do not invent task costs.

## Confluence-safe output

The clean DOCX must use real Word Heading styles, black visible text, Normal paragraphs and simple Table Grid tables. Do not use text boxes, shapes, nested tables, one-cell callouts or semantic colors. The document must import into Confluence without relying on Word colors.

## Output

Create:
- normalized report-data JSON;
- working DOCX with source comments;
- clean DOCX without source comments;
- sources JSON.

The DOCX must remain exactly four A4 landscape pages. Validate layout after rendering.

## Payments

Plan comes from the contract/DS. Keep the existing evidence levels:
- `official` -> `Оплачен`;
- `project_confirmed` -> `Подтвержден`;
- `provisional` -> `Требует подтверждения`;
- `missing` -> derive `Не наступил срок` / `Не оплачен` / `Требует подтверждения` without inventing a date.

Payment statuses are not work statuses and must never be normalized through the four-status work lifecycle.

## Source traceability

Preserve source IDs for every material fact. Generate a working DOCX with source comments and a clean DOCX without comments. Keep visible wording client-readable; do not expose phrases such as `найдено в чате`, `по памяти LLM`, or internal confidence labels.

## Risks and consistency

Use `РИСК` for a future uncertain event, `ПРОБЛЕМА` for a realized event, and `ОТКЛОНЕНИЕ` for a measured difference from baseline. Reconcile unresolved risks from the previous ОСП.

Before rendering, run the existing consistency pass:
- a confirmed payment cannot coexist with an open request to confirm the same payment;
- an open schedule deviation must be reflected in control question #2;
- an open technical problem must be reflected in control question #5;
- any open risk/problem/deviation must be reflected in control question #7;
- risks describe impact, open items describe the action/decision.

## Incremental runs

When prior `report-data.json`, `sources.json`, and `source-manifest.json` exist outside the repository, reuse unchanged normalized facts and process only changed/new evidence. Do not store real project state in the skill repository.

## Optional Confluence publishing

If the packaged runtime contains the existing Confluence publisher, keep using it only on explicit user request and only after DOCX validation. Credentials remain outside the repository. The clean DOCX structure itself must be import-safe even when the user imports it manually.

## Generation workflow

1. Determine report scope and continuity from the prior ОСП/state.
2. If a previous ОСП exists, capture its section order and table structures before generating any new layout; use it as the document template. If it does not exist, load the built-in fallback structure from `references/report-structure.md`.
3. Read contract and every applicable DS before operational evidence.
4. Extract project passport, project start date, active DS/stages, task baseline and payment plan.
5. Overlay factual statuses/dates from confirmed project evidence without replacing unchanged contractual rows or redesigning inherited tables.
6. Normalize all work statuses to the four-status lifecycle.
7. Calculate weighted progress without parent/child double counting.
8. Build risks/open items and run consistency validation.
9. Render/update working and clean DOCX using the inherited structure or fallback template.
10. Visually inspect all four pages and verify no clipping/overflow.
11. Return DOCX files and normalized JSON/source manifests.
