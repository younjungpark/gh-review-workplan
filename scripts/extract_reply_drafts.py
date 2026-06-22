#!/usr/bin/env python3
"""Extract Reply Drafts blocks from a review workplan markdown file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gh_review_workplan.markdown import extract_fenced_drafts


def extract_reply_drafts(markdown: str) -> list[dict[str, str]]:
    drafts = extract_fenced_drafts(markdown, "Reply Drafts", "comment_id")
    return [{"comment_id": draft["comment_id"], "body": draft["body"]} for draft in drafts]


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
