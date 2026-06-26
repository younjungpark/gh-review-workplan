# PR 123 Review Authoring Workplan

Captured: 2026-06-26 Asia/Seoul

Target PR: https://github.com/example/app/pull/123

Scope: file-backed review authoring. Do not post GitHub review comments from this document unless explicitly requested.

## Source Data

- GitHub diff snapshot: `review/raw/pr-123.diff`
- GitHub changed files: `review/raw/pr-123-files.json`
- Local branch: `review/pr-123`
- Local HEAD during analysis: `abc1234`

## Current PR Snapshot

- State: open
- Review decision: pending local review workplan
- Mergeability: unknown
- Base: `main`
- Head: `feature/token-refresh`
- Changed files: 4

## Review Scope

- Included: token refresh endpoint, session middleware, auth tests
- Excluded: generated lockfile changes
- Reviewer stance: bug/risk focused; avoid noisy style-only comments unless requested.

## Candidate Findings

| priority | finding_id | path | line | side | status | confidence | rationale |
|---|---|---|---:|---|---|---|---|
| P1 | F-001 | `src/auth/session.ts` | 87 | RIGHT | ready | high | Expired refresh tokens appear to be accepted when the cache entry still exists. |
| P2 | F-002 | `tests/auth/session.test.ts` | 142 | RIGHT | ready | medium | Tests cover valid refresh tokens but not expired-token rejection. |
| P3 | F-003 | `src/auth/session.ts` | 31 | RIGHT | dropped | low | Naming suggestion only; not worth posting as a review comment. |

## Ready Comments

### `F-001`

- path: `src/auth/session.ts`
- line: 87
- side: RIGHT
- priority: P1
- confidence: high

```text
This path appears to trust the cached refresh-token entry without re-checking the token expiry. If an expired token remains in the cache, it can still create a new session.

Could we verify the expiry before issuing the replacement session, and add a regression test for an expired refresh token that is still present in the cache?
```

### `F-002`

- path: `tests/auth/session.test.ts`
- line: 142
- side: RIGHT
- priority: P2
- confidence: medium

```text
Could we add a regression test for an expired refresh token? The current cases cover valid refresh and invalid token format, but I do not see coverage for the expiry boundary that protects the session-creation path.
```

## Dropped / Not Posting

| finding_id | reason |
|---|---|
| F-003 | Naming preference only; does not identify a concrete bug or regression risk. |

## Review Bundles

### Bundle A: Refresh-token expiry safety

Primary findings:

- `F-001`: `src/auth/session.ts:87`
- `F-002`: `tests/auth/session.test.ts:142`

Reviewer intent:

- Ensure expired refresh tokens cannot create new sessions, even if stale cache data exists.

Suggested direction:

1. Check token expiry before session creation.
2. Add an expired-token regression test.
3. Confirm existing valid-token refresh behavior still passes.

Evidence:

```bash
npm test -- session.test.ts
```

Result:

- Pending. Run after the author updates the PR or before posting if local test setup is available.

## Submit Plan

- Event: PENDING
- Summary body: Two auth-session findings, focused on refresh-token expiry handling and regression coverage.
- Findings to post:
  - `F-001`
  - `F-002`

## Stop Point

No GitHub review comments were posted from this document.
