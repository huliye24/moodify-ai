# P05 Test Plan

- [ ] TST-01 source integrity
- [ ] TST-02 invalid audio
- [ ] TST-03 optional stem bypass
- [ ] TST-04 external API transient mapping
- [ ] TST-05 judgment BYPASS
- [ ] TST-06 profile version binding
- [ ] TST-07 render provenance
- [ ] TST-08 verification failure guard
- [ ] TST-09 stale lease before upload
- [ ] TST-10 production fingerprint replay
- [ ] TST-11 scratch cleanup
- [ ] TST-12 no secret logging
- [ ] TST-13 stage result completeness
- [ ] TST-14 object registration
- [ ] TST-15 no direct READY mutation

## Integration

One authorized/test audio input:

`RUNNING job → CompletionCandidate`

Must record:

- job/attempt IDs
- pipeline version
- stage timeline
- artifacts
- evidence
- resource summary
- verification verdict
