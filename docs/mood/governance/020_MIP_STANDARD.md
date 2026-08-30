# MIP Standard — MOOD Improvement Proposal Format

> MIP-000 itself is the governance process specification.

Every MIP document — both as a registry record and as a Markdown source —
must contain the following sections.

## Required Sections

```text
MIP Number
Title
Status
Category
Authors
Created
Updated
Summary
Motivation
Specification
Rationale
Security Considerations
Backward Compatibility
Implementation Plan
Open Questions
Decision Record
Implementation References
```

## Additional Sections for Economics / Token Categories

For MIPs whose category is `economics`, `treasury`, or `token`, the document
must also include:

```text
Economic Risks
Parameter Table
Launch Gate Dependencies
```

These additional sections are part of the public record. They are NOT used to
trigger automatic on-chain action.

## Format Rules

- The `MIP Number` is the canonical id (`MIP-000`, `MIP-001`, …).
- The `Title` is a short, descriptive name used in public lists.
- The `Status` must be one of: `draft`, `discussion`, `review`, `accepted`,
  `rejected`, `implemented`, `withdrawn`, `superseded`, `archived`.
- The `Category` must be one of the controlled vocabularies defined in
  `apps/web/lib/mood/governance/types.ts`.
- The `Authors` is an array of Resident IDs (NOT wallet addresses).
- `Created` and `Updated` are ISO-8601 timestamps.
- `Summary` is a one-paragraph overview that fits in a public list view.
- `Motivation` explains why the MIP is needed.
- `Specification` describes the proposed change in concrete terms.
- `Rationale` explains why this approach over alternatives.
- `Security Considerations` enumerates risks and mitigations.
- `Backward Compatibility` describes how the change interacts with existing
  canon / policy / data.
- `Implementation Plan` lists the concrete steps to apply the change.
- `Open Questions` lists unresolved issues.
- `Decision Record` lists all recorded decisions (accepted, rejected,
  returned-for-revision).
- `Implementation References` lists commit SHAs, PR URLs, deployed routes,
  or policy doc paths that prove the implementation actually happened.

## Source / Provenance

If a MIP is sourced from a Markdown file in `docs/mood/governance/`, the
record MUST carry:

- `sourcePath` — repository-relative path to the source file.
- `sourceSha` — the SHA-256 hash of the source file at registration time.

If no source file exists (e.g. registry-only draft), leave both empty.
The public API never fabricates these.

## Versioning

`supersedes` and `supersededBy` are populated when a new MIP replaces an
older one. Superseded MIPs are never deleted from the registry; they remain
publicly readable as historical record.
