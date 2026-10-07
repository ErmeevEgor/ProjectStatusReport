# Internal LLM prompt — Project Status Report v0.8

Build normalized `report-data.json` from project evidence. Preserve source traceability and use deterministic rules for calculations and validation.


## Output mode selection

Before layout work, detect the primary output mode.

- If a previous ОСП Confluence Storage Format file is supplied, use `confluence_storage`.
  - Read `references/confluence-storage-format.md`.
  - Use the supplied Storage Format as the primary structural template.
  - Return `confluence-storage.xml`.
  - Do not require DOCX or four-page visual QA unless DOCX is separately requested.
- Otherwise use `docx` and keep the existing four-page working/clean DOCX workflow.
- If both are explicitly requested, render both independently from the same normalized report data.

Never use DOCX import as an intermediate step for native Confluence macros.

## Previous-first continuity

If a previous ОСП exists, use it for factual continuity. For document structure, use the previous Confluence Storage Format in `confluence_storage` mode; otherwise use the previous clean/readable ОСП in `docx` mode.

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

In `confluence_storage` mode, dedicated dates use native `<time datetime="YYYY-MM-DD" />`. Handy Status numeric IDs may only be reused from the supplied previous Storage Format; never invent them. Treat textual Handy `Status` parameters as non-authoritative when they conflict with numeric IDs.

## Incremental state

If external `report-data.json`, `sources.json`, `source-manifest.json` exist, reuse unchanged facts and process only changed evidence.

Structural baseline:
- `confluence_storage` -> supplied previous Storage Format;
- `docx` -> previous clean/readable DOCX.
