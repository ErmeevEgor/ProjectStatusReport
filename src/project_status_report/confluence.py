from __future__ import annotations

import argparse
import base64
import getpass
import json
import mimetypes
import os
import re
import secrets
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph


def _iter_blocks(document: DocumentObject) -> Iterable[Paragraph | Table]:
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            yield Paragraph(child, document)
        elif tag == "tbl":
            yield Table(child, document)


def docx_to_confluence_storage(path: Path) -> str:
    """Convert the skill's Confluence-safe DOCX subset to storage XHTML."""
    document = Document(path)
    parts: list[str] = []
    list_tag: str | None = None

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            parts.append(f"</{list_tag}>")
            list_tag = None

    for block in _iter_blocks(document):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                close_list()
                continue
            style = str(block.style.name or "")
            if style.startswith("List"):
                wanted = "ol" if "Number" in style else "ul"
                if list_tag != wanted:
                    close_list()
                    list_tag = wanted
                    parts.append(f"<{list_tag}>")
                parts.append(f"<li>{escape(text)}</li>")
                continue
            close_list()
            heading = re.match(r"Heading\s+([1-6])", style, flags=re.IGNORECASE)
            if heading:
                level = heading.group(1)
                parts.append(f"<h{level}>{escape(text)}</h{level}>")
            else:
                parts.append(f"<p>{escape(text)}</p>")
            continue

        close_list()
        parts.append("<table><tbody>")
        for row_index, row in enumerate(block.rows):
            cell_tag = "th" if row_index == 0 else "td"
            parts.append("<tr>")
            for cell in row.cells:
                text = "\n".join(p.text.strip() for p in cell.paragraphs if p.text.strip())
                value = escape(text).replace("\n", "<br />") or "&#160;"
                parts.append(f"<{cell_tag}>{value}</{cell_tag}>")
            parts.append("</tr>")
        parts.append("</tbody></table>")

    close_list()
    return "".join(parts)


def latest_report_page(
    pages: Iterable[dict[str, Any]], title_pattern: str = r"(?i)\bОСП\b"
) -> dict[str, Any] | None:
    pattern = re.compile(title_pattern)
    candidates = [
        page
        for page in pages
        if pattern.search(str(page.get("title") or ""))
        and "шаблон" not in str(page.get("title") or "").lower()
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda page: (
            str((page.get("version") or {}).get("when") or ""),
            int((page.get("version") or {}).get("number") or 0),
        ),
    )


@dataclass
class ConfluenceClient:
    base_url: str
    token: str = field(repr=False)
    user: str | None = None
    auth_mode: str = "auto"

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if self.auth_mode == "auto":
            self.auth_mode = "basic" if self.user else "bearer"
        if self.auth_mode not in {"basic", "bearer"}:
            raise ValueError("auth_mode must be auto, basic, or bearer")
        if self.auth_mode == "basic" and not self.user:
            raise ValueError("Basic authentication requires a user")

    def _authorization(self) -> str:
        if self.auth_mode == "bearer":
            return f"Bearer {self.token}"
        raw = f"{self.user}:{self.token}".encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("ascii")

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = {
            "Authorization": self._authorization(),
            "Accept": "application/json",
        }
        request_headers.update(headers or {})
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            request_headers["Content-Type"] = "application/json; charset=utf-8"
        request = Request(
            self.base_url + path,
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=60) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise RuntimeError(f"Confluence HTTP {exc.code}: {detail}") from exc
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def get_page(self, page_id: str) -> dict[str, Any]:
        expand = urlencode({"expand": "space,version,ancestors,body.storage"})
        return self._request("GET", f"/rest/api/content/{page_id}?{expand}")

    def list_child_pages(self, parent_id: str) -> list[dict[str, Any]]:
        start = 0
        results: list[dict[str, Any]] = []
        while True:
            query = urlencode({"limit": 100, "start": start, "expand": "version,history"})
            page = self._request(
                "GET", f"/rest/api/content/{parent_id}/child/page?{query}"
            )
            batch = list(page.get("results") or [])
            results.extend(batch)
            if len(batch) < int(page.get("limit") or 100):
                break
            start += len(batch)
        return results

    def create_child_page(
        self,
        parent_id: str,
        title: str,
        storage_html: str,
        *,
        space_key: str | None = None,
    ) -> dict[str, Any]:
        if not space_key:
            space_key = str((self.get_page(parent_id).get("space") or {}).get("key") or "")
        if not space_key:
            raise RuntimeError("Cannot determine Confluence space key")
        payload = {
            "type": "page",
            "title": title,
            "ancestors": [{"id": str(parent_id)}],
            "space": {"key": space_key},
            "body": {"storage": {"value": storage_html, "representation": "storage"}},
        }
        return self._request("POST", "/rest/api/content", payload=payload)

    def upload_attachment(self, page_id: str, file_path: Path) -> dict[str, Any]:
        boundary = "----ProjectStatusReport" + secrets.token_hex(12)
        media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        prefix = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{file_path.name}\"\r\n"
            f"Content-Type: {media_type}\r\n\r\n"
        ).encode("utf-8")
        suffix = f"\r\n--{boundary}--\r\n".encode("ascii")
        body = prefix + file_path.read_bytes() + suffix
        return self._request(
            "POST",
            f"/rest/api/content/{page_id}/child/attachment",
            body=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "X-Atlassian-Token": "no-check",
            },
        )


def _client_from_args(args: argparse.Namespace) -> ConfluenceClient:
    base_url = args.base_url or os.environ.get("CONFLUENCE_BASE_URL")
    user = args.user or os.environ.get("CONFLUENCE_USER")
    token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not base_url:
        raise ValueError("Set --base-url or CONFLUENCE_BASE_URL")
    if not token:
        token = getpass.getpass("Confluence API token: ")
    if not token:
        raise ValueError("Confluence API token is required")
    return ConfluenceClient(base_url, token, user=user, auth_mode=args.auth)


def _page_url(client: ConfluenceClient, page: dict[str, Any]) -> str:
    links = page.get("_links") or {}
    if links.get("base") and links.get("webui"):
        return str(links["base"]).rstrip("/") + str(links["webui"])
    return f"{client.base_url}/pages/viewpage.action?pageId={page.get('id')}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read or publish Project Status Reports in Confluence.")
    parser.add_argument("--base-url", help="Confluence base URL")
    parser.add_argument("--user", help="Confluence username for Basic auth")
    parser.add_argument("--auth", choices=["auto", "basic", "bearer"], default="auto")
    subparsers = parser.add_subparsers(dest="command", required=True)

    latest = subparsers.add_parser("latest", help="Find the latest child OSP page")
    latest.add_argument("--parent-id", required=True)
    latest.add_argument("--title-pattern", default=r"(?i)\bОСП\b")

    publish = subparsers.add_parser("publish", help="Create a new child page from a clean DOCX")
    publish.add_argument("--parent-id", required=True)
    publish.add_argument("--title", required=True)
    publish.add_argument("--docx", required=True, type=Path)
    publish.add_argument("--space-key")
    publish.add_argument("--attach", action="store_true")
    publish.add_argument(
        "--confirm-publish",
        action="store_true",
        help="Required acknowledgement for the external write",
    )
    args = parser.parse_args(argv)

    if args.command == "publish" and not args.confirm_publish:
        print("Refusing to publish without --confirm-publish", file=sys.stderr)
        return 2

    client = _client_from_args(args)
    if args.command == "latest":
        page = latest_report_page(client.list_child_pages(args.parent_id), args.title_pattern)
        print(json.dumps(page, ensure_ascii=False, indent=2))
        return 0 if page else 1

    storage_html = docx_to_confluence_storage(args.docx)
    page = client.create_child_page(
        args.parent_id,
        args.title,
        storage_html,
        space_key=args.space_key,
    )
    if args.attach:
        client.upload_attachment(str(page["id"]), args.docx)
    print(
        json.dumps(
            {"id": page.get("id"), "title": page.get("title"), "url": _page_url(client, page)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
