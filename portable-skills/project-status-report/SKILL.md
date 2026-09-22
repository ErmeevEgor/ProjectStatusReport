---
name: project-status-report
description: Build a four-page project status report (ОСП) from project context, exported chats, contracts, additional agreements, prior status reports, task trackers, acts and payment evidence. Use when the user needs to create or update an ОСП, validate its completeness, calculate weighted progress by budget, or prepare plan/fact payments without inventing unsupported facts.
---

# Project Status Report

Create and update a four-page project status report (ОСП) from project evidence.

The skill must preserve factual traceability. Never replace missing project data with plausible assumptions.

When the user asks how to connect or use the skill, read [USER_GUIDE.md](USER_GUIDE.md).

## Mandatory first step: previous ОСП

Before building a report, determine whether a previous ОСП exists.

- If a previous ОСП is already attached or present in project context, use it.
- If the user explicitly says that no previous ОСП exists, proceed and create report №1.
- If neither is true, ask the user for the previous ОСП **before final generation**.
- Do not repeatedly ask after the user has answered.

Use the previous ОСП for continuity of:
- report number;
- reporting period;
- open risks;
- open questions;
- unfinished tasks;
- prior deviations and corrective actions.

Do not treat an old ОСП as stronger evidence than a later signed document or later confirmed project fact.

## Required evidence

Use all available project evidence that is relevant:

1. current project/chat context;
2. exported Telegram/Slack/email chat;
3. signed contract;
4. signed additional agreements;
5. acts / UPD / acceptance evidence;
6. payment evidence;
7. previous ОСП;
8. task tracker / Bitrix24 / Confluence / Jira;
9. meeting minutes and project documents.

If the host can access a project workspace or connected files, search them before claiming that data is missing.

Read [references/source-priority.md](references/source-priority.md) before resolving conflicts.

## Do not invent facts

Distinguish:

- `confirmed`: supported by an authoritative source;
- `provisional`: supported only by project communication or an indirect source;
- `missing`: no evidence;
- `conflict`: two relevant sources disagree and cannot be reconciled safely.

For `missing` and `conflict`, do not guess.

Visible report text must be client-readable. Do not write service phrases such as:
- "по контексту проекта";
- "по памяти LLM";
- "найдено в чате";
- "нужно проверить вручную".

Store source details in traceability metadata and Word comments in the working version.

## Output: exactly four pages

The DOCX must contain exactly four pages in this order:

1. **Резюме по проекту**
2. **Данные по задачам**
3. **Риски проекта**
4. **Ключевые вопросы и проблемы**

Read [references/report-structure.md](references/report-structure.md) for the required fields and layout.

Use A4 landscape orientation, compact tables, fixed column widths, and page breaks between sections. Page 3 must fit within page margins.

## Overall project status

The field **"Общий статус проекта"** must be more detailed than a single sentence.

Write 4–6 concise management points covering:
1. current phase / stage;
2. key results completed in the reporting period;
3. current focus / next stage;
4. schedule deviation or confirmation that there is none;
5. financial/payment state;
6. the most important blocker, dependency, risk, or decision.

Do not duplicate the full task table.

## Plan and fact

Contract / additional agreement defines the baseline plan:
- scope;
- stage boundaries;
- dates;
- duration;
- budget;
- deliverables;
- payment plan and payment triggers.

Project context and operational evidence defines the fact:
- task statuses;
- actual dates;
- actual acceptance;
- open issues;
- current risks;
- actual payments.

Never use a chat message to overwrite a signed contractual baseline.

## Page 2 contractual baseline

Page 2 is a contractual baseline table. Rows shown on page 2 must come from the
signed contract or the latest applicable signed additional agreement. Operational
trackers define factual status, actual dates, current result, and comments, but
must not replace contractual rows, budgets, or baseline dates.

Use the lowest explicitly costed contractual level that covers the approved
budget without counting both a parent and its children. Put only those rows in
`tasks`. Put tracker tasks, technical backlog, internal assignments, and customer
or contractor actions in `operational_items`; they do not appear on page 2 and do
not participate in progress.

If a costed child has no explicit dates and belongs unambiguously to a contractual
parent with a defined period, inherit that period and set
`date_basis=parent_stage_period`. Otherwise use `date_basis=missing`.

## Progress calculation

Calculate progress by budget, not by task count.

Canonical coefficients:

- completed / agreed / accepted = `1.00`;
- on approval / on acceptance = `0.90`;
- in progress = `0.50`;
- not started = `0.00`.

Read [references/progress-calculation.md](references/progress-calculation.md).

Do not double count parent and child tasks.

Use the lowest costing level that:
1. has explicit costs in evidence;
2. covers the entire contract stage;
3. sums to the approved stage budget.

If task-level costs are absent, do not invent equal distribution. Use stage-level costs.

## Plan/fact payments

Plan must come from contract / additional agreement.

For each payment capture:
- payment name;
- amount;
- percentage if defined;
- contractual trigger;
- contractual deadline;
- planned date if directly specified or safely derivable;
- actual payment status;
- actual date;
- confirmation level.

Fact priority:
1. accounting/bank/official payment document;
2. explicit project message about payment, marked `provisional`;
3. otherwise `missing`.

In the clean report use normal status wording:
- `Оплачен`;
- `Не оплачен`;
- `Требует подтверждения`;
- `Не наступил срок`.

Do not show the source wording in the main report.

## Source traceability

Every material fact should have a source record where possible.

The normalized JSON must preserve:
- source type;
- source name;
- date;
- location/reference;
- optional note;
- confidence level.

Generate two DOCX variants:
- `working`: source comments included;
- `clean`: comments removed.

Also output `sources.json`.

Read [references/traceability.md](references/traceability.md).

## Risks

Do not mix future risks with already realized problems.

Use:
- `РИСК` for a future uncertain event;
- `ПРОБЛЕМА` for an event already realized;
- `ОТКЛОНЕНИЕ` for a measured deviation from baseline.

A realized problem does not have a probability of occurrence; use `Реализовано` or `—`.

Before page 3, perform a separate risk coverage pass:

- review overdue incomplete contractual tasks;
- review blockers and dependencies affecting the next milestone;
- review material high/medium open questions and operational incidents;
- reconcile every unresolved risk from the previous ОСП;
- classify each material candidate as `РИСК`, `ПРОБЛЕМА`, or `ОТКЛОНЕНИЕ`;
- link it to related task and open-item IDs, then deduplicate by impact.

Do not require a fixed number of risks; require complete coverage. Read
[references/risk-identification.md](references/risk-identification.md) before
building pages 3 and 4.

## Key questions and health check

The question "Есть открытые риски проекта?" is derived from page 3:
- any non-closed material risk/problem -> `Да`;
- none -> `Нет`.

Do not let pages 3 and 4 contradict each other.

Open questions table must contain:
- open question/action;
- required decision/action;
- responsible;
- due date;
- status/result.

## Generation workflow

1. Gather all relevant evidence.
2. Ask for previous ОСП if required.
3. Extract the current contractual hierarchy and select the lowest complete costing level.
4. Create contractual `tasks`; keep operational work in `operational_items`.
5. Extract prior-report continuity.
6. Process project chat and exported messages chronologically and overlay factual status.
7. Reconcile facts using source priority.
8. Build open items, then perform the mandatory risk coverage pass.
9. Create `report-data.json` according to [schema/report-data.schema.json](schema/report-data.schema.json).
10. Run validation and progress calculation.
11. Fix model errors by re-checking evidence; do not alter facts merely to pass validation.
12. Generate working and clean DOCX.
13. Render both DOCX files and visually inspect every page.
14. Ensure exactly four pages, no clipped text, and no tables outside margins.
15. Return:
    - clean DOCX;
    - working DOCX when useful;
    - normalized JSON;
    - brief summary of what was filled and what remains unconfirmed.

## Runtime

When filesystem and execution tools are available, run:

```text
python <skill-dir>/runtime/project_status_report/cli.py <report-data.json> --out <output-dir>
```

The packaged runtime requires Python 3.11+ and `python-docx>=1.2.0`.

When a host has its own high-quality DOCX creation tools, it may use them instead, but all business rules and validation rules in this skill remain mandatory.

## User interaction

- Do not ask the user to run terminal commands when the host can do it.
- Ask only for missing evidence that materially blocks correctness.
- After generation, briefly state:
  - what was filled automatically;
  - what could not be confirmed;
  - which fields still require manual confirmation.
