# Pipeline Stage Contract

## Common Stage Result

Required:

- stage
- status: SUCCEEDED / BYPASSED / FAILED
- job_id
- attempt_id
- input_objects
- output_objects
- evidence_refs
- metrics
- decision
- producer
- producer_version
- started_at
- finished_at

## Stage Registry

| Stage | Required | Inputs | Outputs | Evidence | Bypass Allowed | Timeout | Retry Safe |
|---|---:|---|---|---|---:|---:|---:|
| ACQUIRE | yes | object refs | local scratch | integrity | no | | yes |
| VALIDATE | yes | local source | metadata | validation | no | | yes |
| STEM | optional | source | stem objects | stem manifest | yes | | depends |
| ANALYZE | yes | source/stems | analysis | metrics | no | | yes |
| JUDGE | yes | analysis | judgment | evidence | no | | yes |
| INTERVENE | optional | source/stems+judgment | transformed | manifest | yes | | depends |
| PROFILE | yes | judgment | profile decision | decision evidence | no | | yes |
| RENDER | yes | selected audio/profile | render candidate | render manifest | no | | depends |
| VERIFY | yes | render/source | verdict | verification evidence | no | | yes |
| REGISTER | yes | durable outputs | object refs | registration evidence | no | | yes |

## Rule

No stage may depend on an unnamed file left somewhere by a previous stage.
