# Moodify AI-Native CLI Architecture v1

Moodify's product boundary is a machine-callable CLI over a testable application core. GUI, web and external DAWs are optional clients or adapters, never the source of truth.

```text
CLI / JSON protocol
        ↓
application use cases
        ↓
canonical project domain
        ↓
typed ports
        ↓
audio, MIDI, score, lyrics and evidence adapters
```

The canonical project owns asset identity and hashes, intent, plans, runs, artifacts and evidence. A backend may disappear without making the project history uninterpretable.

Production commands follow `inspect → plan → execute → verify`. Planning is non-destructive. Execution requires an explicit plan, verifies source identity before processing, writes only to a new output directory and persists the run. Verification re-hashes both source and output.

The v1 vertical slice intentionally exposes only a minimal native render: one referenced audio source and a bounded gain node. Capabilities must describe this limit. Track timelines, buses, automation and full mastering are not production capabilities until separately implemented and accepted.

Dependency direction is domain → application → ports → adapters, with CLI invoking application use cases. During migration, the implementation remains a strangler façade around existing Moodify modules; old commands are retained.

