# PR <PR_NUMBER> Review Authoring Workplan

Captured: <YYYY-MM-DD timezone>

Target PR: <PR_URL>

Scope: file-backed review authoring. Do not post GitHub review comments from this document unless explicitly requested.

## Source Data

- GitHub diff snapshot: `review/raw/pr-<PR_NUMBER>.diff`
- GitHub changed files: `review/raw/pr-<PR_NUMBER>-files.json`
- Local branch:
- Local HEAD during analysis:

## Current PR Snapshot

- State:
- Review decision:
- Mergeability:
- Base:
- Head:
- Changed files:

## Review Scope

- Included:
- Excluded:
- Reviewer stance: bug/risk focused; avoid noisy style-only comments unless requested.

## Candidate Findings

| priority | finding_id | path | line | side | status | confidence | rationale |
|---|---|---|---:|---|---|---|---|
| P1 | F-001 | `path/to/File.java` | 1 | RIGHT | candidate | high | Short technical summary. |

## Ready Comments

### `F-001`

- path: `path/to/File.java`
- line: 1
- side: RIGHT
- priority: P1
- confidence: high

```text
Paste-ready review comment.
```

## Dropped / Not Posting

| finding_id | reason |
|---|---|
| F-000 | Duplicate, stale, style-only, or too low confidence. |

## Review Bundles

### Bundle A: <Name>

Primary findings:

- `F-001`: `path/to/File.java:1`

Reviewer intent:

- Concrete risk in technical terms.

Suggested direction:

1. Suggested fix or question.

Evidence:

```bash
command
```

Result:

- Pending or concrete evidence.

## Submit Plan

- Event: PENDING
- Summary body:
- Findings to post:
  - `F-001`

## Stop Point

No GitHub review comments were posted from this document.
