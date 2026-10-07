# Confluence Storage Format mode

Use this reference only when the user supplies a previous ОСП page exported as Confluence Storage Format and expects the next ОСП as Storage Format for manual insertion through Confluence Source Editor.

## Trigger

Enable `confluence_storage` mode only when an attached file is clearly the Storage Format of a previous ОСП page.

Typical evidence:
- Confluence storage XHTML/XML fragment;
- `<ac:structured-macro ...>`;
- `<time datetime="YYYY-MM-DD" />`;
- ОСП tables/sections matching the previous report.

Do not treat ordinary HTML, Markdown, DOCX or PDF as Storage Format merely because they contain tables.

If no Storage Format is supplied, do not use this mode. Use the normal DOCX workflow.

If the user explicitly requests both outputs, generate both independently from the same normalized `report-data.json`.

## Structural continuity

The supplied Storage Format is the primary structural template for the Confluence output.

Preserve, where compatible:
- section order and section names;
- tables and their order;
- column set and order;
- row grouping;
- `class`, `style`, widths and other harmless layout attributes;
- existing Confluence macros;
- the logical four-section ОСП hierarchy.

Update data inside the inherited structure instead of redesigning the page.

When a previous DOCX is supplied together with Storage Format:
- Storage Format has structural precedence for Confluence output;
- DOCX may still be used as a continuity/factual source;
- do not render DOCX unless the user also requests it.

## Output

Primary file:
- `confluence-storage.xml`

The file is a Confluence Storage Format fragment ready to paste into Source Editor. It is not a standalone web page and does not need `<html>` / `<body>` wrappers.

Do not publish the page automatically unless the user separately requests publication and an authorized Confluence connector/API is available.

The four-page DOCX pagination rule does not apply in this mode.

Always keep semantic validation, contractual progress rules, payment rules, risks, continuity and source traceability.

## Dates

Dates in dedicated semantic fields must use native Confluence date markup:

```xml
<time datetime="2026-10-09" />
```

A date range uses two native date elements:

```xml
<time datetime="2026-10-03" />–<time datetime="2026-10-06" />
```

Use native dates for dedicated date fields such as:
- report date / reporting period;
- project start date;
- plan/fact start;
- plan/fact end;
- payment fact date;
- risk date;
- action due date;
- next control milestone date.

Dates embedded in narrative prose or comments remain ordinary text unless the inherited template already uses a native date there.

Never invent a missing date.

## Handy Status

When the previous Storage Format uses Handy Status, preserve Handy Status rather than replacing it with the standard Confluence `status` macro.

Observed storage form:

```xml
<ac:structured-macro
    ac:macro-id="239743da-52bc-4b1e-9ec6-070c1d996501"
    ac:name="status-handy"
    ac:schema-version="1">
  <ac:parameter ac:name="Status">В РАБОТЕ</ac:parameter>
  <ac:parameter ac:name="id">2941</ac:parameter>
</ac:structured-macro>
```

### Authoritative field

For Handy Status in this project workflow:

- `<ac:parameter ac:name="id">...</ac:parameter>` is authoritative for the rendered Handy Status state;
- the textual `<ac:parameter ac:name="Status">...</ac:parameter>` is not authoritative and may be stale;
- changing only `Status` text is not sufficient;
- never invent a Handy Status `id`.

### Build a reusable status pool

Parse all `status-handy` macros from the previous Storage Format.

Record at least:
- `id`;
- `ac:macro-id`;
- textual `Status` parameter;
- section/table;
- column semantic;
- row/entity context.

Separate pools by semantic domain. At minimum:
- work lifecycle statuses;
- payment statuses;
- risk probability;
- risk impact;
- risk processing/state.

Do not mix IDs from different semantic domains merely because the labels look similar.

### Reusing statuses

For a continuing row/entity whose status did not change:
- preserve the complete existing Handy Status macro block whenever possible.

When a status must change:
- reuse an existing, safely identified `id` that already represents the required state in the same semantic domain;
- synchronize the textual `Status` parameter for readability, but do not rely on it for rendering;
- do not create numeric IDs by incrementing, guessing or copying an unrelated domain.

A reused Handy Status ID may be referenced on a new page when the user's Confluence instance has been manually verified to keep pages independent. This project has such a manual verification; still do not infer new IDs.

### Conflicts and ambiguity

If the same Handy `id` occurs with conflicting textual `Status` labels:
- treat the textual labels for that ID as unreliable;
- do not derive a canonical state from those labels alone;
- prefer positional preservation for the corresponding continuing row;
- for changed/new rows, choose a different unambiguous ID from the same domain if available.

If the required Handy Status value cannot be safely represented from the supplied template:
- do not fabricate an ID;
- render the intended status as plain readable text in that cell;
- add an XML comment immediately after it:
  `<!-- HANDY_STATUS_ID_REQUIRED: <target status> -->`;
- include the same unresolved mapping in source/state notes when available.

This fallback is preferable to a visually plausible but semantically wrong Handy Status.

### `ac:macro-id`

`ac:macro-id` identifies the Confluence macro occurrence.

- For an unchanged inherited macro occurrence, preserve the existing `ac:macro-id`.
- For a newly inserted macro occurrence, generate a new UUID v4.
- Do not duplicate one `ac:macro-id` across newly created macro occurrences.

The Handy numeric `id` and `ac:macro-id` are different identifiers and must not be confused.

## Work status semantics

The ОСП business lifecycle remains exactly:
- `Не начато`;
- `В работе`;
- `На согласовании`;
- `Выполнено`.

The normalized status in `report-data.json` remains the business truth used for progress calculation.

The Confluence renderer maps that normalized status to an inherited Handy Status ID only at presentation time.

Payment statuses and risk attributes are separate status domains and are never normalized through the four work statuses.

## Storage Format validation

Before returning `confluence-storage.xml`, verify:

1. The logical ОСП section order is preserved.
2. Contract/task progress is identical to normalized report data.
3. No parent/child double counting was introduced.
4. Every dedicated date that has a value uses ISO `YYYY-MM-DD` inside `<time datetime="..."/>`.
5. No missing date was invented.
6. Every emitted Handy Status numeric `id` came from the supplied previous Storage Format.
7. New `ac:macro-id` values are UUID v4 and unique.
8. Conflicting Handy text labels were not treated as authoritative.
9. XML/XHTML special characters in text are escaped.
10. The result is a Confluence Storage Format fragment suitable for Source Editor.
11. No DOCX-specific four-page validation is applied in this mode.

## Recommended filename

`ОСП_<report_number>_Confluence_Storage_Format.xml`
