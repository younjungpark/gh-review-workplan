# gh-review-workplan

Codex skill for managing GitHub pull request reviews as file-backed workplans.

This skill supports a small review workplan family:

- Incoming response mode: collect thread-aware review data, group incoming comments into work bundles, keep paste-ready reply drafts, and optionally post replies back to GitHub after explicit approval.
- Outgoing authoring mode: collect PR diff context, track candidate findings, keep ready-to-post review comment drafts, and optionally create a pending or submitted GitHub review after explicit approval.

## Contents

- `SKILL.md` - skill instructions
- `templates/review-plan.md` - incoming response workplan template
- `templates/author-plan.md` - outgoing review authoring workplan template
- `scripts/fetch_review_threads.py` - fetch PR review threads with `gh api graphql`
- `scripts/fetch_pr_diff.py` - fetch PR diff and changed-file metadata
- `scripts/extract_reply_drafts.py` - extract reply drafts from a workplan
- `scripts/post_reply_drafts.py` - dry-run or post reply drafts
- `scripts/extract_review_drafts.py` - extract outgoing review drafts from a workplan
- `scripts/submit_review_drafts.py` - dry-run or create a pending/submitted PR review
- `references/github-review-api.md` - GitHub review API notes

## Basic Usage

Copy or install this folder into a Codex skills directory, such as:

```bash
~/.codex/skills/gh-review-workplan
```

Then ask Codex to create or update a GitHub review workplan for a PR.

GitHub writes are dry-run by default. Reply and review submission scripts require `--apply` before they write to GitHub.

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
