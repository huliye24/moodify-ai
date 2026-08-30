# MOOD CONTRIBUTION 016 — Evidence Policy

**Authority:** 016 TASK.md Phase E

## Validation rules

| Type | Validation |
|------|-----------|
| `url` | Must parse as URL. Scheme must be `http:` or `https:`. ≤ 2048 chars. |
| `github-pr` / `github-commit` | URL host must be `github.com` or `www.github.com`. ≤ 2048 chars. |
| `document` / `artifact` | ≤ 5000 chars reference string. |
| `text` | ≤ 5000 chars. |

## Banned

- `javascript:` — XSS / phishing vector.
- `data:` — payload smuggling.
- `file:` — local file access.
- Any non-HTTP(S) scheme.

## Caps

- At most 20 evidence items per submission.
- Each evidence item has length cap by type (see table).
- Labels ≤ 200 chars.

## Why these rules

- Resident must see real URLs only — no shorteners / opaque data URLs that
  could redirect to phishing.
- GitHub-specific types help reviewers verify provenance quickly.
- String-length caps prevent trivial DoS.

## Implementation

`apps/web/lib/mood/contribution/evidence.ts` exports `validateEvidence(input)`
and `isValidEvidenceArray(items)`. Both return `{ ok: true } | { ok: false, code, message }`.

`Registry.createSubmission` calls `isValidEvidenceArray` on the input. The API
layer propagates `code` and `message` to the client for transparent error reporting.