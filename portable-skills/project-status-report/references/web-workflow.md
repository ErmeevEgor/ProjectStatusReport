# Web workflow: Google Drive state → Confluence Storage XML

This is the canonical execution environment for Project Status Report v0.9+.

## Contract with the user

Input:

- exact Google Drive project folder URL;
- project/context evidence in Drive;
- optional attachments and project links supplied in the conversation;
- persistent `report-data.json` and `sources.json` when already created;
- previous ОСП Storage Format XML.

Output:

- updated `report-data.json` in the same Drive folder;
- updated `sources.json` in the same Drive folder;
- new `ОСП_<N>_Confluence_Storage_Format.xml` returned to the user.

Do not upload the XML to Drive by default.

## Drive discovery

1. Open the exact user-supplied folder.
2. Locate exact filenames `report-data.json` and `sources.json`.
3. Inspect relevant project files and subfolders that are available.
4. Prefer direct connector reads for Drive-native/private content.
5. Do not use public web search as a substitute for inaccessible private Drive files.

## Read order

Read in this order:

1. previous Storage Format XML;
2. current `report-data.json`;
3. current `sources.json`;
4. signed contract and applicable signed DS needed to confirm baseline;
5. acts/UPD/payment evidence;
6. project task/status evidence;
7. minutes/correspondence/new attachments/links.

The purpose of this order is continuity first, then baseline, then current fact.

## Update strategy

Do not regenerate semantic state from zero on every run when valid state exists.

Start from existing state, then apply evidence changes:

- keep unchanged facts;
- update changed facts;
- add new facts/sources;
- close or transform previously open items only with evidence;
- preserve old source records needed for audit/history.

## Drive write-back

For each state file:

1. identify its exact Drive file ID;
2. serialize valid UTF-8 JSON;
3. replace existing raw content in place when supported;
4. preserve filename and folder;
5. read back or verify metadata after write.

Do not create `report-data (1).json`, dated copies or a new file on every run.

If an existing state file cannot be updated in place but upload is possible, use the safest overwrite/replacement capability available and verify that only one canonical state file remains.

## Links outside Drive

User-supplied links can be evidence.

- Drive/Docs links: use the Drive connector when available.
- Public project pages: fetch the exact supplied URL.
- Do not broaden into unrelated web research unless the user asks for verification/research.

Record useful source URL/reference information in `sources.json` without exposing access tokens or private connector internals.

## Failure handling

### Previous XML missing

Stop normal rendering. Do not invent a new page structure and do not fall back to DOCX.

### State JSON missing

Reconstruct state conservatively from previous XML + strongest project evidence, then create the missing state files in Drive.

### Drive read unavailable

Do not pretend project evidence was inspected. Use only evidence actually available and flag the limitation.

### Drive write unavailable

Return XML and both updated JSON files to the user, and explicitly state that Drive was not updated.

## Completion criteria

A web run is complete only when:

- semantic state is reconciled;
- XML is rendered and validated;
- both state JSONs are written back and verified, or write failure is explicitly reported;
- XML is returned to the user;
- XML has not been uploaded to Drive unless explicitly requested.
