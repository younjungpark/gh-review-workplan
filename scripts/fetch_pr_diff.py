#!/usr/bin/env python3
"""Fetch GitHub PR diff and changed-file metadata with gh."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_gh(args: list[str]) -> str:
    result = subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True)
    return result.stdout


def fetch_changed_files(repo: str, pr: int) -> list[dict]:
    files: list[dict] = []
    page = 1
    while True:
        batch = json.loads(
            run_gh([
                f"repos/{repo}/pulls/{pr}/files",
                "-F",
                "per_page=100",
                "-F",
                f"page={page}",
            ])
        )
        files.extend(batch)
        if len(batch) < 100:
            return files
        page += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="pull request number")
    parser.add_argument("--out-dir", default="review/raw", type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    diff_path = args.out_dir / f"pr-{args.pr}.diff"
    files_path = args.out_dir / f"pr-{args.pr}-files.json"

    diff = run_gh([
        f"repos/{args.repo}/pulls/{args.pr}",
        "-H",
        "Accept: application/vnd.github.v3.diff",
    ])
    files = fetch_changed_files(args.repo, args.pr)

    diff_path.write_text(diff, encoding="utf-8")
    files_path.write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding="utf-8")
    print(diff_path)
    print(files_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
