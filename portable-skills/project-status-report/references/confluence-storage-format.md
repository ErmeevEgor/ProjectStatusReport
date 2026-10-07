# Confluence Storage Format — recurring ОСП

The previous ОСП Storage Format XML/XHTML is the mandatory structural template for the next recurring report.

## Output

Return a Confluence Storage Format fragment named:

`ОСП_<report_number>_Confluence_Storage_Format.xml`

It is intended for manual insertion through Confluence Source Editor.

Do not wrap it in `<html>` or `<body>`.

Do not generate DOCX and do not convert from DOCX.

## Structural continuity

Preserve where compatible:

- section order and names;
- tables and table order;
- columns and column order;
- row grouping;
- `class`, `style`, widths and harmless layout attributes;
- existing Confluence macros;
- logical four-section ОСП hierarchy.

Update values inside the inherited structure instead of redesigning the page.

## Native dates

Dedicated dates must use native Confluence markup:

```xml
<time datetime="2026-10-09" />
```

A range uses two native date elements:

```xml
<time datetime="2026-10-03" />–<time datetime="2026-10-06" />
```

Use native dates for dedicated report/project/stage/payment/risk/action date fields whenever a real date exists.

Dates embedded in narrative prose may remain text unless the inherited template already uses native date markup there.

Never invent a date.

## Handy Status

Preserve `status-handy` when it exists in the previous XML.

Typical form:

```xml
<ac:structured-macro ac:macro-id="239743da-52bc-4b1e-9ec6-070c1d996501" ac:name="status-handy" ac:schema-version="1">
  <ac:parameter ac:name="Status">В РАБОТЕ</ac:parameter>
  <ac:parameter ac:name="id">2941</ac:parameter>
</ac:structured-macro>
```

### Numeric ID is authoritative

`<ac:parameter ac:name="id">...</ac:parameter>` determines the Handy Status rendering.

The text `Status` parameter may be stale and is not authoritative by itself.

Never invent a Handy numeric ID.

### Build status pools from the previous XML

Parse all `status-handy` macros and record:

- numeric `id`;
- `ac:macro-id`;
- textual `Status`;
- section/table;
- column semantic;
- row/entity context.

Keep separate semantic pools at minimum for:

- work lifecycle;
- payment state;
- risk probability/fact;
- risk impact;
- risk processing/state.

Never reuse an ID across semantic domains merely because labels look similar.

### Unchanged status

For a continuing row whose status did not change, preserve the complete inherited Handy Status macro whenever possible.

### Changed/new status

When status changes:

- use only an unambiguous numeric ID already observed for the required state in the same semantic domain;
- synchronize the textual `Status` parameter for readability;
- for a new macro occurrence generate a unique UUID v4 `ac:macro-id`.

Do not duplicate a newly generated `ac:macro-id` across occurrences.

### Ambiguous/unavailable mapping

If the same numeric ID appears with conflicting text labels, do not infer its state from text alone.

If the required state cannot be represented safely from the previous XML, render plain readable text and immediately add:

```xml
<!-- HANDY_STATUS_ID_REQUIRED: <target status> -->
```

This is safer than fabricating a numeric ID.

## Work lifecycle

Normalized business truth remains exactly:

- `Не начато`;
- `В работе`;
- `На согласовании`;
- `Выполнено`.

The Confluence renderer maps these normalized values to inherited Handy IDs only at presentation time.

Payment and risk status domains remain separate.

## Validation

Before returning XML verify:

1. inherited logical section order is preserved;
2. visible task/progress data equals `report-data.json`;
3. no contractual parent/child double counting exists;
4. every dedicated date with a value uses ISO `YYYY-MM-DD` inside `<time datetime="..." />`;
5. no missing date was invented;
6. every emitted Handy numeric ID appeared in the supplied previous XML;
7. newly generated `ac:macro-id` values are unique UUID v4;
8. conflicting Handy text labels were not treated as authoritative;
9. XML special characters are escaped;
10. output is a Confluence Storage Format fragment suitable for Source Editor.
