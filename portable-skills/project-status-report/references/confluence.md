# Confluence

Confluence is an optional source and delivery target. Use it only when the user
authorizes reading or publishing project data. DOCX generation must work without
Confluence.

## Credentials

Never store a username, password, API token, cookie, or Authorization header in
the repository, report JSON, DOCX, source manifest, logs, or command history.

Supported sources, in priority order:

1. `CONFLUENCE_BASE_URL`, `CONFLUENCE_USER`, `CONFLUENCE_API_TOKEN`;
2. a per-project local profile supplied with `--config` or
   `PROJECT_STATUS_REPORT_CONFLUENCE_CONFIG`;
3. hidden interactive token input.

On Windows, create a local profile outside the repository. The token is encrypted
with DPAPI for the current Windows user:

```text
python <skill-dir>/scripts/publish_confluence.py \
  --config <external-state-dir>/confluence.local.json \
  --base-url <url> --user <user> --auth basic configure
```

The command asks for the token through hidden input. The JSON profile contains
only connection metadata and DPAPI ciphertext; it cannot be decrypted by another
Windows account. Do not copy it into Git.

## Reading the current state

Treat a supplied folder page as the parent. List its direct child pages and
select the latest page whose title matches `ОСП` by `version.when`, not by title
number alone. Exclude pages whose title contains `Шаблон`.

```text
python <skill-dir>/scripts/publish_confluence.py \
  --config <external-state-dir>/confluence.local.json \
  latest --parent-id <page-id>
```

Reading Confluence for continuity is optional. Prefer existing external project
state when it already contains the normalized prior report.

## Publishing a new page

Generate and visually verify the clean DOCX first. Create a child page only when
the user asked for a new report page:

```text
python <skill-dir>/scripts/publish_confluence.py \
  --config <external-state-dir>/confluence.local.json \
  publish --parent-id <page-id> --title <title> --docx <clean.docx> \
  --attach --confirm-publish
```

## Updating an existing page

When correcting a page that was already created for the same report, update that
explicit page instead of creating a duplicate:

```text
python <skill-dir>/scripts/publish_confluence.py \
  --config <external-state-dir>/confluence.local.json \
  publish --page-id <existing-page-id> --docx <clean.docx> \
  --attach --confirm-publish
```

The client increments the page version and replaces an attachment with the same
filename, or uploads it when absent. It converts only the supported subset:
headings, ordinary paragraphs, lists, and simple tables.

External writes require explicit user authorization and `--confirm-publish`.
Never publish the working DOCX or private JSON. Return the final page URL and
verify its parent when creating a new page.
