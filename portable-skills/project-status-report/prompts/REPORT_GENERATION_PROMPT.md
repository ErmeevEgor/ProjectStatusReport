# Internal LLM prompt — Project Status Report v0.9

Run the canonical **web LLM + Google Drive + previous Confluence Storage Format** workflow.

## Inputs

Expect:

- an exact Google Drive project folder URL;
- project/context evidence in Drive, attachments and user-supplied links;
- existing `report-data.json` and `sources.json` in the project folder when available;
- previous ОСП as Confluence Storage Format XML/XHTML.

The previous XML is the structural template. There is no DOCX branch.

## Required result

1. Update normalized semantic state from current evidence.
2. Replace/update `report-data.json` in the same Drive folder.
3. Replace/update `sources.json` in the same Drive folder.
4. Render `ОСП_<N>_Confluence_Storage_Format.xml` from the previous XML structure and return it to the user.
5. Do not upload the XML to Drive unless explicitly requested.

## Evidence and continuity

- Read current state first.
- Read the previous XML for report number/date, unresolved items, structure, macros and Handy Status pool.
- Read contractual baseline before applying operational facts.
- Read project changes from Drive/attachments/supplied links.
- Reconcile by source authority and chronology.
- Increment report number and carry unresolved items forward unless newer evidence closes/transforms them.
- Never invent facts, dates, costs, statuses or Handy Status IDs.

## State persistence

Treat `report-data.json` and `sources.json` as persistent project state.

Preserve stable source IDs. Add only genuinely new evidence. Update existing facts and confidence when stronger evidence resolves them.

If state files already exist, update them in place by Drive file ID when supported. Do not create duplicate copies.

If Drive write fails, return both JSONs as fallback files and explicitly say Drive was not updated.

## Work lifecycle

Visible work statuses are exactly:

- Не начато
- В работе
- На согласовании
- Выполнено

Use fixed coefficients 0 / 0.5 / 0.9 / 1.0 and budget-weighted progress. Never double-count parent and child contractual costs. Operational items do not participate.

## Confluence rendering

Preserve the previous XML's compatible section/table/column/grouping/layout structure.

Dedicated dates use native `<time datetime="YYYY-MM-DD" />`.

For Handy Status:

- numeric `id` is authoritative;
- reuse only numeric IDs observed in the previous XML and only inside the same semantic domain;
- preserve unchanged inherited macro blocks where possible;
- new macro occurrences require unique UUID v4 `ac:macro-id`;
- if no safe numeric ID exists, use plain text plus `<!-- HANDY_STATUS_ID_REQUIRED: ... -->`.

Do not generate HTML wrappers. Output a Confluence Storage Format fragment suitable for Source Editor.

## Validation

Before final output verify:

- XML, `report-data.json` and `sources.json` describe the same project state;
- contractual scope/budget/payment plan were not overwritten by weaker evidence;
- progress has no parent/child double count;
- payments and open actions do not contradict;
- prior open risks/items were reconciled;
- all native date values are real ISO dates;
- all Handy numeric IDs came from the previous XML;
- Drive state update succeeded or failure is explicitly reported;
- XML was not uploaded to Drive by default.
