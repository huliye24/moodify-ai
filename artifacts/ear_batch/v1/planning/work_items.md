# Verifiable Work Items

| Work item | Epic | Risk | Dependencies |
|---|---|---|---|
| WI-001 Define SourceIdentity JSON Schema | EPIC-01 | safe | none |
| WI-002 Define MeasurementRecord JSON Schema | EPIC-01 | safe | WI-001 |
| WI-003 Define EvidenceArtifact JSON Schema | EPIC-01 | safe | WI-001, WI-002 |
| WI-004 Define Judgment and Uncertainty schemas | EPIC-01 | safe | WI-002, WI-003 |
| WI-005 Create Ear v1 contract validator CLI | EPIC-06 | safe | WI-001, WI-002, WI-003, WI-004 |
| WI-006 Build provenance manifest utility | EPIC-06 | safe | WI-001 |
| WI-007 Define controlled WSE experiment manifest | EPIC-03 | safe | WI-002, WI-003 |
| WI-008 Add deterministic synthetic fixture definitions | EPIC-03 | safe | WI-007 |
| WI-009 Define experimental before-after comparison contract | EPIC-03 | safe | WI-002, WI-003, WI-007 |
| WI-010 Define experimental ProductionCase record | EPIC-04 | safe | WI-003, WI-004 |
| WI-011 Design listening-review authority vocabulary | EPIC-05 | human-review | WI-004, WI-010 |
| WI-012 Create traceability integrity checker | EPIC-06 | safe | WI-005 |
