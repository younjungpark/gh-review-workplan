#!/usr/bin/env python3
"""Extract Reply Drafts blocks from a review workplan markdown file."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEADING_RE = re.compile(r"^###\s+`?(\d+)`?\s*$")
FENCE_RE = re.compile(r"^```(?:text)?\s*$")


def extract_reply_drafts(markdown: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    in_reply_section = False
    current_id: str | None = None
    collecting = False
    body: list[str] = []
    drafts: list[dict[str, str]] = []

    def flush() -> None:
        nonlocal current_id, body
        if current_id and body:
            drafts.append({"comment_id": current_id, "body": "\n".join(body).strip()})
        body = []

    for line in lines:
        if line.startswith("## "):
            if in_reply_section:
                if collecting:
                    flush()
                break
            in_reply_section = line.strip() == "## Reply Drafts"
            continue

        if not in_reply_section:
            continue

        match = HEADING_RE.match(line)
        if match:
            if collecting:
                flush()
            current_id = match.group(1)
            collecting = False
            body = []
            continue

        if current_id and FENCE_RE.match(line):
            if collecting:
                flush()
                collecting = False
                current_id = None
            else:
                collecting = True
            continue

        if collecting:
            body.append(line)

    return drafts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args()

    drafts = extract_reply_drafts(args.plan.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(drafts, ensure_ascii=False, indent=2))
    else:
        for draft in drafts:
            print(f"### {draft['comment_id']}")
            print(draft["body"])
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
