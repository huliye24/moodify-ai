# Cross-Lane Requests

Per `MOODIFY_THINKPAD_HEAVY_LANE_001` §24: changes to mainline-owned surfaces are
**not** made from the heavy lane; they are recorded here for the mainline machine.

---

## CLR-001 — CLI help text still says "The Ear of AI"

```text
file:     moodify-core-package/src/moodify/release_cli.py (argparse description)
need:     update the CLI program description to the current canonical identity.
reason:   `moodify --help` prints "Moodify — The Ear of AI". That public identity was
          superseded by Canon v2.1 (2026-09-23); Ear is internal-only. Found while
          walking the real CLI surface for the PROCESS pipeline verification.
status:   NON_BLOCKING
suggest:  one-line string change, but it is product-narrative language — a mainline
          decision. No behavior effect.
```

## CLR-002 — `docs/development/README.md` is stale

```text
file:     docs/development/README.md
need:     refresh or archive. It still describes apps/web/ as an active system and
          "Cloud Production 001" as the next step (2026-08-24 boundaries), all
          superseded by the 2026-10-03 restructure and Canon v3.
reason:   discovered while adding the heavy-lane documents to docs/development/.
status:   NON_BLOCKING
suggest:  mainline rewrites it as the dev-entry index; the heavy-lane docs added here
          (THINKPAD_*) are self-contained.
```
