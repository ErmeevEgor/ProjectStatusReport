# External project state

## `report-data.json`
Primary normalized semantic project/report state: passport, contract/DS baseline, stages/tasks, dates/statuses, payments, risks and open actions.

## `sources.json`
Evidence/source registry and derived-fact traceability.

## `source-manifest.json`
Local technical fingerprint manifest: absolute path, filename, size, mtime and SHA256. It is used only to detect added/changed/unchanged/missing raw local files.

It is not semantic state and is not required for rendering.

## Local agent
Keep all three files in a persistent project-state folder outside Git. Use the manifest to re-read only changed sources.

## Web LLM
Normally attach `report-data.json` + `sources.json`. Do not normally attach `source-manifest.json`, because uploaded file paths are temporary and differ from local absolute paths.

## Structural templates are separate

| File | Role |
|---|---|
| `report-data.json` | semantic state |
| `sources.json` | evidence traceability |
| `source-manifest.json` | local change detection |
| previous Storage Format | Confluence structural/macro template |
| previous clean DOCX | DOCX structural template |
