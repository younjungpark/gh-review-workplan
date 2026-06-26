---
name: gh-review-workplan
description: Use when managing GitHub pull request reviews as file-backed workplans, including incoming reviewer comments, outgoing review findings, reply drafts, inline review drafts, grouped fixes, or verification notes.
---

# GitHub Review Workplan

## Overview

Use this skill when a PR review needs more structure than direct browser-based handling. Keep GitHub review state in local markdown, preserve raw data, and make every GitHub write optional and explicit.

This is a review workplan family with two modes:

| mode | use when | local id | GitHub write |
|---|---|---|---|
| Incoming response | addressing comments left on your PR | `comment_id` | reply to an existing review comment |
| Outgoing authoring | reviewing someone else's PR | `finding_id` | create a pending or submitted PR review |

**Companion skill:** Use `github:gh-address-comments` for incoming review context and thread-aware reading conventions. For outgoing reviews, use GitHub PR metadata, changed files, and diff context before drafting comments.

## Core Workflow

Shared steps:

1. Resolve the PR owner, repository, PR number, base/head, and current branch.
2. Fetch the relevant raw data before analysis.
3. Save raw artifacts under `review/raw/`.
4. Create or update a markdown workplan from the matching template.
5. Group work by behavior area, risk, or review theme, not merely by file.
6. Put final GitHub-facing text in a top-level draft section, not inside tables.
7. Record tests, logs, source evidence, and exact verification commands in the plan.
8. Write to GitHub only when the user explicitly asks for that exact action.

Incoming response mode:

1. Fetch thread-aware review data with GitHub GraphQL via `gh api graphql`; do not rely only on flat REST comments for unresolved/outdated state.
2. Use `templates/review-plan.md`.
3. Exclude resolved, outdated, duplicate, or already-answered comments from the active plan.
4. Track each active comment by `comment_id`, URL, path, line, status, and analysis.
5. Implement fixes one bundle or one comment at a time.
6. Put paste-ready response text under `## Reply Drafts`.

Outgoing authoring mode:

1. Fetch PR metadata, changed files, and diff context.
2. Use `templates/author-plan.md`.
3. Track possible issues by local `finding_id`, path, line, side, priority, confidence, and rationale.
4. Move only high-signal findings into `## Ready Comments`.
5. Keep noisy, stylistic, duplicate, or low-confidence notes under `## Dropped / Not Posting`.
6. Prefer one pending review containing all approved inline comments over many immediate single comments.

## Status Values

Incoming response statuses:

- `unresolved, active`: needs analysis or code work.
- `in progress`: currently being handled.
- `resolved locally`: code/docs/tests and reply draft are ready locally.
- `posted`: reply was posted to GitHub.
- `deferred`: intentionally not handled now, with reason.
- `obsolete`: resolved/outdated/duplicated by newer thread.

Outgoing authoring statuses:

- `candidate`: needs verification before becoming a real review comment.
- `ready`: high-signal comment draft is ready locally.
- `dropped`: intentionally not posting, with reason.
- `posted`: review comment was posted to GitHub.
- `stale`: diff location no longer matches the current PR head.

## Files

Incoming response layout:

```text
review/
  raw/
    pr-<number>-review-threads.json
    pr-<number>-review-threads.md
  pr-<number>-review-plan.md
```

Outgoing authoring layout:

```text
review/
  raw/
    pr-<number>.diff
    pr-<number>-files.json
  pr-<number>-author-plan.md
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

Fetch diff data for outgoing review authoring:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/fetch_pr_diff.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --out-dir review/raw
```

Extract outgoing review drafts:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/extract_review_drafts.py \
  review/pr-12765-author-plan.md
```

Dry-run outgoing review creation:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/submit_review_drafts.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --plan review/pr-12765-author-plan.md
```

Actually create the pending or submitted review only after explicit user approval:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/submit_review_drafts.py \
  --repo hibernate/hibernate-orm \
  --pr 12765 \
  --plan review/pr-12765-author-plan.md \
  --event PENDING \
  --apply
```

## Reply Safety

Before posting incoming replies:

- Refresh the PR review thread snapshot.
- Confirm each `comment_id` still belongs to the target PR.
- Check whether the bot/user already replied after the reviewer comment.
- Run in dry-run mode first and show the exact comment IDs and bodies.
- Use `--apply` only after the user explicitly asks to submit replies.

Never resolve threads, submit reviews, or post top-level PR comments unless the user asks for that exact write action.

## Review Authoring Safety

Before posting outgoing review comments:

- Refresh PR metadata and diff data.
- Confirm every `finding_id` still maps to a valid file, line, and side on the current PR head.
- Remove duplicate findings already covered by existing comments or reviews.
- Drop low-confidence, preference-only, or stylistic comments unless the user explicitly wants them.
- Run in dry-run mode first and show the exact findings, paths, lines, event, and bodies.
- Use `--apply` only after the user explicitly asks to submit the review.

Prefer `PENDING` for first writes so the user can inspect the draft review in GitHub before submitting.

## Common Mistakes

- Using REST review comments alone and losing thread resolution state. Use GraphQL review threads for triage.
- Keeping long reply drafts in a table. Put them under `## Reply Drafts`.
- Keeping outgoing review comments in a candidate table only. Put final review text under `## Ready Comments`.
- Editing code before preserving raw review data. Save `review/raw/` first.
- Treating the plan as a replacement for verification. The plan must record commands and evidence, but tests still need to run.
- Posting replies from stale markdown. Refresh GitHub state before writes.
- Submitting noisy review comments. Prefer fewer high-signal comments with concrete risk, evidence, and suggested fixes.
