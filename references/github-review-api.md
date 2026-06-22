# GitHub Review API Notes

## Incoming Review Replies

Use GraphQL `pullRequest.reviewThreads` when resolution or outdated state matters. Flat REST review comments do not fully represent review-thread state.

Useful REST endpoint for replying to an inline review comment:

```text
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies
```

`comment_id` is the numeric pull request review comment database id, such as `3441298676`.

Use `gh api` for the reply:

```bash
gh api \
  --method POST \
  repos/OWNER/REPO/pulls/PR/comments/COMMENT_ID/replies \
  -f body='reply text'
```

Guardrails:

- Dry-run first.
- Re-fetch thread state before posting.
- Do not post if a later reply from the PR author already exists.
- Do not resolve threads unless explicitly requested.

## Outgoing Review Authoring

Useful REST endpoint for creating a PR review with inline comments:

```text
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

The request can contain `body`, `event`, and a `comments` array. Each inline comment needs `path`, `body`, and either diff `position` or modern line metadata such as `line` and `side`. Use `PENDING` locally to mean omitting `event`; GitHub creates a pending review that can be inspected before submission.

Use `gh api` for a review write:

```bash
gh api \
  --method POST \
  repos/OWNER/REPO/pulls/PR/reviews \
  --input payload.json
```

Guardrails:

- Dry-run first.
- Re-fetch the PR diff before posting.
- Confirm every file, line, and side still applies to the latest PR head.
- Prefer one pending review over many immediate single comments.
- Do not submit `COMMENT`, `REQUEST_CHANGES`, or `APPROVE` unless explicitly requested.

Reference: GitHub REST "Create a review for a pull request" documents `event`, `comments`, `path`, `body`, `position`, `line`, `side`, `start_line`, and `start_side`.
