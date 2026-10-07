# Persistent project state for the web workflow

## `report-data.json`

Primary normalized semantic project/report state:

- passport;
- contractual baseline;
- stages/tasks;
- dates/statuses;
- payments;
- risks;
- control answers;
- open actions;
- source references.

This file persists between ОСП runs and is updated in place in the project Google Drive folder.

## `sources.json`

Persistent evidence/source registry used for audit and derived-fact traceability.

Preserve stable source IDs for already known evidence. Add new IDs only for new evidence. Do not silently remove historical source records that still explain carried-forward facts.

## Structural state is separate

The previous ОСП Storage Format XML is not semantic state. It is the structural/macro template for the next Confluence report and the continuity source for prior visible content.

## Web workflow

Persistent project state is:

```text
Google Drive project folder/
├── report-data.json
├── sources.json
└── project evidence...
```

The previous ОСП XML may be attached to the current chat rather than stored in Drive.

There is no required `source-manifest.json` in the web workflow.
