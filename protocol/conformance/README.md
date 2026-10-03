# protocol/conformance/

Tests that decide whether an implementation conforms to the Moodify Sound Protocol.

## Purpose

The protocol is only real if an independent implementation can be checked against it. A
specification with no conformance suite is a description of what the author's code happens
to do.

Conformance tests must therefore:

- be runnable against an implementation that shares no code with Core;
- assert only what the specification actually states;
- fail loudly when the specification is ambiguous, rather than picking an interpretation.

## Current state

**No conformance suite exists yet.** This is recorded rather than hidden. The protocol has a
normative specification and a reference runtime
(`moodify-core-package`, `moodify protocol validate|process`), but third-party
implementations cannot yet be certified.

Establishing a conformance suite is proposed as future work. It is a natural first
substantive MIP after governance.

## What conformance does not cover

Conformance proves that an implementation produces the **shape and execution semantics** the
protocol requires — a valid job is accepted, a malformed one is rejected, an artifact
carries the declared hashes and parameters.

It does **not** prove that the audio is good, or that a preset is appropriate. Perceptual
quality is a matter for human review and the Review Network, not for a conformance gate. See
[`../../docs/governance/NETWORK.md`](../../docs/governance/NETWORK.md).
