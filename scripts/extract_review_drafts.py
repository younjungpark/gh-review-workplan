#!/usr/bin/env python3
"""Extract Ready Comments blocks from a review authoring workplan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from gh_review_workplan.markdown import extract_fenced_drafts


REQUIRED_METADATA = ("path", "line", "side")
INTEGER_METADATA = ("line", "start_line")


def normalize_review_draft(draft: dict[str, Any]) -> dict[str, Any]:
    metadata = draft.get("metadata", {})
    missing = [key for key in REQUIRED_METADATA if not metadata.get(key)]
    if missing:
        finding_id = draft.get("finding_id", "<unknown>")
        raise ValueError(f"{finding_id}: missing metadata: {', '.join(missing)}")

    normalized = {
        "finding_id": draft["finding_id"],
        "body": draft["body"],
        "path": metadata["path"],
        "side": metadata["side"].upper(),
    }
    for key in INTEGER_METADATA:
        if key in metadata:
            try:
                normalized[key] = int(metadata[key])
            except ValueError as exc:
                raise ValueError(f"{draft['finding_id']}: {key} must be an integer") from exc
    for key in ("start_side", "priority", "confidence"):
        if key in metadata:
            normalized[key] = metadata[key]
    return normalized


def extract_review_drafts(markdown: str) -> list[dict[str, Any]]:
    drafts = extract_fenced_drafts(markdown, "Ready Comments", "finding_id")
    return [normalize_review_draft(draft) for draft in drafts]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args()

    try:
        drafts = extract_review_drafts(args.plan.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(drafts, ensure_ascii=False, indent=2))
    else:
        for draft in drafts:
            print(f"### {draft['finding_id']}")
            print(f"{draft['path']}:{draft['line']} {draft['side']}")
            print(draft["body"])
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
