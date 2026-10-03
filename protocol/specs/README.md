# protocol/specs/

Normative specifications for the Moodify Sound Protocol.

## Current

The specification text is maintained in `docs/protocol/` so that existing references and
external links keep resolving. This directory exists to hold **normative text as the
protocol grows**, and to make the protocol layer's structure legible.

| Version | Document | Status |
|---|---|---|
| 0.1 | [`docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`](../../docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md) | Normative |
| 0.2 | [`docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md`](../../docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md) | Normative |

## Adding a specification

A new or changed specification is a protocol change and requires a MIP — see
[`../mips/`](../mips/). Write the MIP first; the specification text follows acceptance.

When you add a document here, register it in the table above and state its status
explicitly. An unregistered specification is indistinguishable from an abandoned draft,
which is how the previous contents of this tree accumulated.

## What the protocol must not become

The protocol describes **jobs, artifacts, parameters, and evidence**. It does not describe
a second implementation of audio processing, and it must not become a place where an
interface hides its own copy of a sound algorithm. See `AGENTS.md`, "One Core, Multiple
Interfaces".
