"""Markdown draft extraction helpers."""

from __future__ import annotations

import re
from typing import Any


HEADING_RE = re.compile(r"^###\s+`?([A-Za-z0-9_.:-]+)`?\s*$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_-]+)?\s*$")
META_RE = re.compile(r"^-\s+([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$")


def clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == "`" and value[-1] == "`":
        return value[1:-1]
    return value


def extract_fenced_drafts(markdown: str, section: str, id_key: str) -> list[dict[str, Any]]:
    lines = markdown.splitlines()
    target_heading = f"## {section}"
    in_section = False
    current_id: str | None = None
    collecting = False
    body: list[str] = []
    metadata: dict[str, str] = {}
    language = ""
    drafts: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal body, metadata, language
        if current_id and body:
            draft: dict[str, Any] = {
                id_key: current_id,
                "body": "\n".join(body).strip(),
            }
            if metadata:
                draft["metadata"] = dict(metadata)
            if language:
                draft["language"] = language
            drafts.append(draft)
        body = []
        metadata = {}
        language = ""

    for line in lines:
        if line.startswith("## "):
            if in_section:
                if collecting:
                    flush()
                break
            in_section = line.strip() == target_heading
            continue

        if not in_section:
            continue

        match = HEADING_RE.match(line)
        if match:
            if collecting:
                flush()
            current_id = match.group(1)
            collecting = False
            body = []
            metadata = {}
            language = ""
            continue

        fence = FENCE_RE.match(line)
        if current_id and fence:
            if collecting:
                flush()
                collecting = False
                current_id = None
            else:
                collecting = True
                language = fence.group(1) or ""
            continue

        if current_id and not collecting:
            meta = META_RE.match(line)
            if meta:
                metadata[meta.group(1)] = clean_value(meta.group(2))
            continue

        if collecting:
            body.append(line)

    return drafts
