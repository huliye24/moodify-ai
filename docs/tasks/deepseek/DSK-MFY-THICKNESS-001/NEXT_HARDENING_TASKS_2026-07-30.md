# Remaining Bridge Work — Ordered Hardening Queue

**Baseline after P0 production-boundary integration:** 2026-07-30  
**Rule:** no new feature work until the current bridge segment reaches its declared gate.

## Completed in the P0 Batch

1. Live Operator Runtime now fails closed unless a structured Rights Manifest authorizes the exact source path and asset ID.
2. Rights evidence is persisted on the Operator Job with verification time.
3. Delivery now requires explicit professional listening approval and an identified approver; MRS cannot grant delivery authority.
4. Delivery records preserve rights and human-approval evidence.
5. Delivery-based Craft writeback now requires an approved technical gate, matching delivery, human approval, and rights evidence.
6. API and CLI surfaces expose explicit rights authorization and approval fields.
7. Legacy tests that depended on implicit approval were converted to evidence-bearing fixtures.

## Next Batch — P0 Automated Writeback Containment

- Inspect `data_loop_runner._writeback_craft()` and `product_integration.write_craft_learning_feed()`.
- Separate unreviewed recommendations from the approved Craft Library namespace.
- Default automated output to `proposal`, never `candidate`, `stable`, or `adopted`.
- Require an explicit promotion operation with rights evidence, human review, source run ID, and regression evidence.
- Add bypass tests for direct function, API, CLI, and repeated execution.

Exit gate: no automated recommendation can appear as reusable approved Craft knowledge without promotion evidence.

## Next Batch — P1 Atomic Generation and Interruption Recovery

- Generate Treatment JSON and Markdown into run-scoped temporary files.
- Validate both artifacts before promotion.
- Atomically replace the pair through a recoverable transaction marker.
- Inject interruption before first promotion, between promotions, and after promotion before cleanup.
- Demonstrate source immutability, deterministic retry, and recovery from every injected point.

Exit gate: every interruption yields either the complete previous pair or the complete new pair; never a mixed pair presented as current.

## Next Batch — P1 Historical Compatibility

- Freeze representative v0.1 Treatment, v2 Workspace, manifest, approval, and delivery fixtures.
- Define supported schema versions.
- Test exact load, migration, preservation of unknown fields, and explicit rejection.
- Preserve original artifacts and produce migration lineage.

Exit gate: every historical fixture loads, migrates with evidence, or fails with a documented actionable reason.

## Final Batch — Independent Load and Succession Review

- Run Runtime, Core, root, recovery, compatibility, and determinism suites.
- Execute duplicate requests and interruption cases.
- Audit evidence links and engineering ledgers.
- Update product history with what became impossible to bypass.
- Perform a second independent acceptance; the implementer does not self-promote.

