# MIP-0000 — MIP Template

```yaml
mip: 0000
title: <short descriptive title>
author: <name or handle>
status: DRAFT
type: <Protocol | Schema | Core-Contract | Governance | Evidence-Format | Compatibility>
created: <YYYY-MM-DD>
requires: <MIP numbers, or none>
supersedes: <MIP numbers, or none>
```

> Copy this file to `MIP-<next-number>-<slug>.md` and fill it in. Do not edit this template
> to make a proposal.

---

## Abstract

One paragraph. What changes, and for whom. A reader should be able to decide from this
paragraph alone whether the rest concerns them.

## Motivation

Why is the current state inadequate? State the **problem**, not the solution. If the problem
cannot be stated without the solution in it, the problem is not yet understood.

Answer explicitly:

- What breaks, or what stays impossible, today?
- Who is affected — Core, CLI, Apps, integrators, the Review Network?
- What is the cost of doing nothing?

## Specification

The precise change. Where it touches a contract, give the exact fields, types, and defaults.
Where it touches behavior, state the observable difference.

```text
<schema, interface, or behavioral delta>
```

## Rationale

Why this design and not the alternatives. Name the alternatives you considered and say what
each costs. Where a trade-off is real, admit which side you chose and why.

## Backwards compatibility

- Does this break existing jobs, artifacts, or schema consumers?
- If yes, what is the migration path, and does it require a protocol version bump?
- What is the rollback?

State "**Breaking, no migration path**" plainly if that is the truth. A proposal that hides
a break in vague language will be rejected at the Evidence stage.

## Evidence

**This section is what separates a MIP from an opinion.** A proposal may be `DRAFT` or
`DISCUSSION` without evidence, but it cannot reach `ACCEPTED` without it.

| What was measured | How | Result | Where the artifact lives |
|---|---|---|---|
| | | | `docs/evidence/…` |

Include, where applicable:

```text
source hash · core version · protocol version · parameters · processing graph
before metrics · after metrics · A/B result · human review
agent version · timestamp · reproducibility
```

If the evidence is insufficient or negative, say so here. **A negative result honestly
recorded is a valid basis for a decision** — including for `REJECTED`. Do not suppress a
counterexample to preserve the proposal; see `ME-002` in
[`docs/governance/constraints/`](../../docs/governance/constraints/CONSTRAINT_REGISTRY.md).

## Human review

Which perceptual claims require human listening judgment, and who reviews them?

Machine authority is scoped. An out-of-scope, insufficient-evidence, or uncertain
perceptual case must produce `HUMAN_REQUIRED` or `INCONCLUSIVE` — it may not be resolved
by suppressing the escalation.

## Reference implementation

Link or describe. A MIP may be accepted before implementation, but `IMPLEMENTED` requires a
reference implementation that passes its own test plan.

## Test plan

How a reader can verify the change independently.

```bash
<exact commands>
```

Prefer a reproduction command over a description of one.

## Security and privacy considerations

Does this touch credentials, private audio, personal data, or the security model in
`security/`? If not, say so explicitly.

## Unresolved questions

List what this proposal does not settle. An empty list here usually means the proposal has
not been examined hard enough.

## Copyright

All MIPs are licensed under GPL-3.0-only, matching this repository.
