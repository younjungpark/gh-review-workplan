# gh-review-workplan

File-backed GitHub PR review workplans for Codex and other coding agents.

Most AI coding tools can read a PR and answer questions interactively. This skill focuses on the missing workflow around that review: preserving the PR context, review findings, reply drafts, verification notes, and ready-to-post GitHub payloads in Markdown so they can be shared, archived, edited, and submitted only after explicit approval.

## Why use this?

Use `gh-review-workplan` when you want a durable Markdown artifact instead of a one-off chat answer.

It is useful for:

- turning a PR diff into a structured review plan before posting comments;
- grouping review findings by risk or behavior area instead of only by file;
- collecting incoming reviewer comments into fix bundles and paste-ready replies;
- keeping raw GitHub snapshots under `review/raw/` for traceability;
- dry-running exact GitHub review/reply payloads before writing anything;
- pasting the result into GitHub, Slack, Notion, an issue, or a team review note.

## Modes

| Mode | Use when | Output | Optional GitHub write |
|---|---|---|---|
| Incoming response | Someone reviewed your PR and you need to address comments | `review/pr-<number>-review-plan.md` | Reply to existing review comments |
| Outgoing authoring | You are reviewing someone else's PR | `review/pr-<number>-author-plan.md` | Create a pending/submitted PR review |

## Contents

- `SKILL.md` - skill instructions
- `templates/review-plan.md` - incoming response workplan template
- `templates/author-plan.md` - outgoing review authoring workplan template
- `examples/sample-author-plan.md` - example outgoing review workplan
- `scripts/fetch_review_threads.py` - fetch PR review threads with `gh api graphql`
- `scripts/fetch_pr_diff.py` - fetch PR diff and changed-file metadata
- `scripts/extract_reply_drafts.py` - extract reply drafts from a workplan
- `scripts/post_reply_drafts.py` - dry-run or post reply drafts
- `scripts/extract_review_drafts.py` - extract outgoing review drafts from a workplan
- `scripts/submit_review_drafts.py` - dry-run or create a pending/submitted PR review
- `references/github-review-api.md` - GitHub review API notes

## Installation

Copy or install this folder into a Codex skills directory, such as:

```bash
~/.codex/skills/gh-review-workplan
```

The helper scripts expect the GitHub CLI (`gh`) to be installed and authenticated for GitHub API access.

```bash
gh auth status
```

## Quick Start: outgoing PR review

Ask Codex or another coding agent to load the skill and create a Markdown review workplan:

```text
Use gh-review-workplan outgoing review mode for owner/repo#123. Analyze the PR diff for bug or regression risks and write review/pr-123-author-plan.md with finding_id-based review comment drafts. Do not post to GitHub yet.
```

The agent should fetch and preserve raw PR context:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/fetch_pr_diff.py \
  --repo owner/repo \
  --pr 123 \
  --out-dir review/raw
```

Then it writes a Markdown workplan like:

````md
# PR 123 Review Authoring Workplan

## Review Scope
- Included: auth middleware, token refresh endpoint, tests
- Reviewer stance: bug/risk focused; avoid noisy style-only comments unless requested.

## Candidate Findings
| priority | finding_id | path | line | side | status | confidence | rationale |
|---|---|---|---:|---|---|---|---|
| P1 | F-001 | `src/auth/session.ts` | 87 | RIGHT | ready | high | Expired refresh tokens can still create a new session. |

## Ready Comments
### `F-001`

- path: `src/auth/session.ts`
- line: 87
- side: RIGHT
- priority: P1
- confidence: high

```text
This branch appears to allow an expired refresh token to create a new session...
```
````

Dry-run the exact GitHub review payload:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/submit_review_drafts.py \
  --repo owner/repo \
  --pr 123 \
  --plan review/pr-123-author-plan.md
```

Actually create a pending review only after explicit approval:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/submit_review_drafts.py \
  --repo owner/repo \
  --pr 123 \
  --plan review/pr-123-author-plan.md \
  --event PENDING \
  --apply
```

## Quick Start: incoming review response

Ask the agent to collect unresolved review comments and produce a response plan:

```text
Use gh-review-workplan for owner/repo#123. Collect unresolved review comments, exclude resolved or outdated threads, and write review/pr-123-review-plan.md. Do not post to GitHub yet.
```

Fetch thread-aware review data:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/fetch_review_threads.py \
  --repo owner/repo \
  --pr 123 \
  --out-dir review/raw
```

Dry-run reply drafts before any write:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/post_reply_drafts.py \
  --repo owner/repo \
  --pr 123 \
  --plan review/pr-123-review-plan.md
```

Post replies only after explicit approval:

```bash
python3 ~/.codex/skills/gh-review-workplan/scripts/post_reply_drafts.py \
  --repo owner/repo \
  --pr 123 \
  --plan review/pr-123-review-plan.md \
  --apply
```

## Natural Language Prompts

Use `gh-review-workplan` in the request when you want Codex to load this skill explicitly.

Incoming review response:

```text
Use gh-review-workplan for owner/repo#123. Collect unresolved review comments, exclude resolved or outdated threads, and write review/pr-123-review-plan.md. Do not post to GitHub yet.
```

Outgoing review authoring:

```text
Use gh-review-workplan outgoing review mode for owner/repo#123. Analyze the PR diff for bug or regression risks and write review/pr-123-author-plan.md with finding_id-based review comment drafts. Do not post to GitHub yet.
```

Dry-run before any write:

```text
Dry-run the Reply Drafts or Ready Comments from the workplan and show me the exact GitHub payload before applying anything.
```

Apply only after explicit approval:

```text
Post the approved Reply Drafts, or create a PENDING review from the approved Ready Comments, using --apply.
```

## Safety defaults

GitHub writes are dry-run by default. Reply and review submission scripts require `--apply` before they write to GitHub. Prefer `PENDING` reviews for first writes so the user can inspect the draft review in GitHub before submitting it.
