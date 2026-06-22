#!/usr/bin/env python3
"""Dry-run or post Reply Drafts from a review workplan markdown file."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from extract_reply_drafts import extract_reply_drafts


def run_gh(repo: str, pr: str, comment_id: str, body: str) -> None:
    endpoint = f"repos/{repo}/pulls/{pr}/comments/{comment_id}/replies"
    subprocess.run(
        ["gh", "api", "--method", "POST", endpoint, "-f", f"body={body}"],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, help="pull request number")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--only", action="append", default=[], help="comment id to post; repeatable")
    parser.add_argument("--apply", action="store_true", help="actually post replies")
    args = parser.parse_args()

    drafts = extract_reply_drafts(args.plan.read_text(encoding="utf-8"))
    if args.only:
        wanted = set(args.only)
        drafts = [draft for draft in drafts if draft["comment_id"] in wanted]

    if not drafts:
        print("No reply drafts found.", file=sys.stderr)
        return 1

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: {len(drafts)} reply draft(s) for {args.repo}#{args.pr}")
    for draft in drafts:
        print(f"\n--- comment {draft['comment_id']} ---")
        print(draft["body"])
        if args.apply:
            run_gh(args.repo, args.pr, draft["comment_id"], draft["body"])

    if not args.apply:
        print("\nDry-run only. Re-run with --apply after explicit user approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
