---
name: gh-review-workplan
description: Use when managing GitHub PR review comments as a file-backed workplan, especially for thread-aware triage, comment_id tracking, reviewer reply drafts, grouped fixes, verification notes, or optional batch posting of inline review replies.
---

# GitHub Review Workplan

## Overview

Use this skill when a PR review needs more structure than direct comment-by-comment handling. Keep GitHub review state in local markdown, use thread-aware data, and make GitHub writes optional and explicit.

**Required companion skill:** Use `github:gh-address-comments` for GitHub review context and thread-aware reading conventions.

## Core Workflow

1. Resolve the PR owner, repository, PR number, base/head, and current branch.
2. Fetch thread-aware review data with GraphQL or the GitHub connector; do not rely only on flat REST comments for unresolved/outdated state.
3. Save raw artifacts under `review/raw/`.
4. Create or update `review/pr-<number>-review-plan.md` from `templates/review-plan.md`.
5. Exclude resolved, outdated, duplicate, or already-answered comments from the active plan.
6. Group active comments into bundles by behavior area, not merely by file.
7. Track each comment by `comment_id`, URL, path, line, status, and analysis.
8. Put reviewer-facing text in the top-level `Reply Drafts` section, not inside tables.
9. Implement fixes one bundle or one comment at a time. Record tests, logs, and exact verification commands in the plan.
10. Post replies only when the user explicitly asks for GitHub writes.

## Status Values

Use consistent statuses:

- `unresolved, active`: needs analysis or code work.
- `in progress`: currently being handled.
- `resolved locally`: code/docs/tests and reply draft are ready locally.
- `posted`: reply was posted to GitHub.
- `deferred`: intentionally not handled now, with reason.
- `obsolete`: resolved/outdated/duplicated by newer thread.

## Files

Default layout:

```text
review/
  raw/
    pr-<number>-review-threads.json
    pr-<number>-review-threads.md
  pr-<number>-review-plan.md
```

Treat `review/` as local operational notes unless the user explicitly wants those files committed.

## Scripts

Use scripts from this skill by absolute path.

Fetch thread-aware data:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/fetch_review_threads.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --out-dir review/raw
```

Extract reply drafts from the plan:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/extract_reply_drafts.py \
  review/pr-12765-review-plan.md
```

Dry-run reply posting:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/post_reply_drafts.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --plan review/pr-12765-review-plan.md
```

Actually post replies only after explicit user approval:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/post_reply_drafts.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --plan review/pr-12765-review-plan.md \
  --apply
```

## Reply Safety

Before posting:

- Refresh the PR review thread snapshot.
- Confirm each `comment_id` still belongs to the target PR.
- Check whether the bot/user already replied after the reviewer comment.
- Run in dry-run mode first and show the exact comment IDs and bodies.
- Use `--apply` only after the user explicitly asks to submit replies.

Never resolve threads, submit reviews, or post top-level PR comments unless the user asks for that exact write action.

## Common Mistakes

- Using REST review comments alone and losing thread resolution state. Use GraphQL review threads for triage.
- Keeping long reply drafts in a table. Put them under `## Reply Drafts`.
- Editing code before preserving raw review data. Save `review/raw/` first.
- Treating the plan as a replacement for verification. The plan must record commands and evidence, but tests still need to run.
- Posting replies from stale markdown. Refresh GitHub state before writes.
