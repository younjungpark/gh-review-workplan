#!/usr/bin/env python3
"""Dry-run or create a GitHub PR review from Ready Comments."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from extract_review_drafts import extract_review_drafts


EVENTS = ("PENDING", "COMMENT", "REQUEST_CHANGES", "APPROVE")


def build_comment(draft: dict[str, Any]) -> dict[str, Any]:
    comment = {
        "path": draft["path"],
        "line": draft["line"],
        "side": draft["side"],
        "body": draft["body"],
    }
    for key in ("start_line", "start_side"):
        if key in draft:
            comment[key] = draft[key]
    return comment


def build_payload(drafts: list[dict[str, Any]], event: str, summary_body: str | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"comments": [build_comment(draft) for draft in drafts]}
    if summary_body:
        payload["body"] = summary_body
    if event != "PENDING":
        payload["event"] = event
    return payload


def run_gh(repo: str, pr: str, payload: dict[str, Any]) -> None:
    endpoint = f"repos/{repo}/pulls/{pr}/reviews"
    subprocess.run(
        ["gh", "api", "--method", "POST", endpoint, "--input", "-"],
        input=json.dumps(payload),
        text=True,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, help="pull request number")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--only", action="append", default=[], help="finding id to post; repeatable")
    parser.add_argument("--event", choices=EVENTS, default="PENDING", help="review event")
    parser.add_argument("--summary-body", help="summary body for COMMENT or REQUEST_CHANGES")
    parser.add_argument("--apply", action="store_true", help="actually create the review")
    args = parser.parse_args()

    if args.event in {"COMMENT", "REQUEST_CHANGES"} and not args.summary_body:
        print(f"error: --summary-body is required for {args.event}", file=sys.stderr)
        return 2

    try:
        drafts = extract_review_drafts(args.plan.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.only:
        wanted = set(args.only)
        drafts = [draft for draft in drafts if draft["finding_id"] in wanted]

    if not drafts:
        print("No review drafts found.", file=sys.stderr)
        return 1

    payload = build_payload(drafts, args.event, args.summary_body)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: {len(drafts)} review draft(s) for {args.repo}#{args.pr} event={args.event}")
    for draft in drafts:
        print(f"\n--- finding {draft['finding_id']} {draft['path']}:{draft['line']} {draft['side']} ---")
        print(draft["body"])

    print("\nPayload:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.apply:
        run_gh(args.repo, args.pr, payload)
    else:
        print("\nDry-run only. Re-run with --apply after explicit user approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
