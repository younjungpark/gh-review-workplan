# GitHub Review API Notes

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
