# gh-review-workplan

Codex skill for managing GitHub pull request review comments as a file-backed workplan.

This skill helps collect thread-aware review data, create a local markdown review plan, group comments into work bundles, keep paste-ready reply drafts, and optionally post replies back to GitHub after explicit approval.

## Contents

- `SKILL.md` - skill instructions
- `templates/review-plan.md` - markdown workplan template
- `scripts/fetch_review_threads.py` - fetch PR review threads with `gh api graphql`
- `scripts/extract_reply_drafts.py` - extract reply drafts from a workplan
- `scripts/post_reply_drafts.py` - dry-run or post reply drafts
- `references/github-review-api.md` - GitHub review API notes

## Basic Usage

Copy or install this folder into a Codex skills directory, such as:

```bash
~/.codex/skills/gh-review-workplan
```

Then ask Codex to create or update a GitHub review workplan for a PR.

Reply posting is dry-run by default. The posting script requires `--apply` before it writes to GitHub.
