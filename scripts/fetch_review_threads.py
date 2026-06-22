#!/usr/bin/env python3
"""Fetch GitHub PR review threads with gh GraphQL and save raw JSON."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


QUERY = """
query($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      number
      title
      state
      reviewDecision
      isDraft
      url
      baseRefName
      headRefName
      baseRefOid
      headRefOid
      reviewThreads(first:100, after:$cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first:50) {
            nodes {
              databaseId
              url
              author { login }
              body
              createdAt
              path
              line
            }
          }
        }
      }
    }
  }
}
"""


def gh_graphql(owner: str, name: str, number: int, cursor: str | None) -> dict:
    cmd = [
        "gh",
        "api",
        "graphql",
        "-f",
        f"query={QUERY}",
        "-F",
        f"owner={owner}",
        "-F",
        f"name={name}",
        "-F",
        f"number={number}",
    ]
    if cursor:
        cmd.extend(["-F", f"cursor={cursor}"])
    else:
        cmd.extend(["-F", "cursor="])
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def fetch_all(repo: str, pr: int) -> dict:
    owner, name = repo.split("/", 1)
    first = gh_graphql(owner, name, pr, None)
    pull = first["data"]["repository"]["pullRequest"]
    threads = pull["reviewThreads"]["nodes"]
    page_info = pull["reviewThreads"]["pageInfo"]
    while page_info["hasNextPage"]:
        page = gh_graphql(owner, name, pr, page_info["endCursor"])
        page_pull = page["data"]["repository"]["pullRequest"]
        threads.extend(page_pull["reviewThreads"]["nodes"])
        page_info = page_pull["reviewThreads"]["pageInfo"]
    pull["reviewThreads"]["nodes"] = threads
    pull["reviewThreads"]["pageInfo"] = page_info
    return first


def write_summary(data: dict, path: Path) -> None:
    pull = data["data"]["repository"]["pullRequest"]
    lines = [
        f"# PR #{pull['number']} Review Threads",
        "",
        f"- Title: {pull['title']}",
        f"- URL: {pull['url']}",
        f"- State: {pull['state']}",
        f"- Review decision: {pull['reviewDecision']}",
        f"- Base: {pull['baseRefName']} `{pull['baseRefOid']}`",
        f"- Head: {pull['headRefName']} `{pull['headRefOid']}`",
        "",
    ]
    for thread in pull["reviewThreads"]["nodes"]:
        comments = thread["comments"]["nodes"]
        first = comments[0] if comments else {}
        lines.extend(
            [
                f"## {first.get('databaseId', thread['id'])}",
                "",
                f"- resolved: {thread['isResolved']}",
                f"- outdated: {thread['isOutdated']}",
                f"- path: `{thread.get('path') or first.get('path')}`",
                f"- line: {thread.get('line') or first.get('line')}",
                f"- url: {first.get('url')}",
                "",
            ]
        )
        for comment in comments:
            body = comment.get("body", "").replace("\n", " ")
            lines.append(f"- {comment['databaseId']} {comment['author']['login']} {comment['createdAt']}: {body}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="pull request number")
    parser.add_argument("--out-dir", default="review/raw", type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    data = fetch_all(args.repo, args.pr)
    json_path = args.out_dir / f"pr-{args.pr}-review-threads.json"
    md_path = args.out_dir / f"pr-{args.pr}-review-threads.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(data, md_path)
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
