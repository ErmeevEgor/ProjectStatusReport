# Confluence

Use Confluence only when the user authorizes reading or publishing project data.

## Credentials

Never store a username, password, API token, cookie, or Authorization header in
the repository, report JSON, DOCX, logs, or command history. Read configuration
from:

- `CONFLUENCE_BASE_URL`;
- `CONFLUENCE_USER` for Basic authentication;
- `CONFLUENCE_API_TOKEN`.

If the token variable is absent, the packaged client requests it with hidden
input. `.env` files are ignored but should not be created unless the user asks.

## Reading the current state

Treat the supplied page as the parent folder. List its direct child pages and
select the latest page whose title matches `ОСП` by `version.when`, not by title
number alone. Exclude pages whose title contains `Шаблон`. Read that page for
continuity before creating a new report.

```text
python <skill-dir>/scripts/publish_confluence.py \
  --base-url <url> --user <user> latest --parent-id <page-id>
```

## Publishing

Generate and visually verify the clean DOCX first. Create a new child page rather
than overwriting the previous ОСП. Convert only the Confluence-safe subset used by
the renderer: headings, ordinary paragraphs, lists, and simple tables. Attach the
clean DOCX when useful.

External writes require explicit user authorization and the
`--confirm-publish` flag:

```text
python <skill-dir>/scripts/publish_confluence.py \
  --base-url <url> --user <user> publish \
  --parent-id <page-id> --title <title> --docx <clean.docx> \
  --attach --confirm-publish
```

After publishing, return the created page URL and verify that the page is a direct
child of the requested parent. Do not publish the working DOCX or private JSON.
