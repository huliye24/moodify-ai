# MFY-CR-P08 — JOB MODEL

## Principle

```text
ReconstructionJob = Product orchestration object
ProductionCase  = Canonical production/evidence authority
```

The job never redefines auditory truth, evidence, case lifecycle, rule
authority, or judgment authority. It references `production_case_id`; the
canonical `production_case.json` + `evidence.json` live in the job workspace.

## Relationships

```text
Owner (actor)
  └── ReconstructionJob (reconstruction_jobs table)
        ├── source_asset_id / source_sha256 (owner-bound upload)
        ├── production_case_id -> ProductionCase (canonical, in workspace)
        │       └── evidence_ids -> EvidenceArtifact[] (canonical, evidence.json)
        └── result_object_id -> ReconstructionResult (reconstruction_results table)
                └── audio_object_ref (path reference; audio body never in DB)
```

## ReconstructionJob fields

`job_id, owner_id, source_asset_id, source_sha256, production_case_id, status,
progress_stage, requested_at, started_at, completed_at, failed_at,
reconstruction_version, result_object_id, result_status, failure_code,
failure_stage, retry_policy, attempts, billing_state_placeholder
(=NOT_IMPLEMENTED), privacy_policy_version (=privacy-policy-v0.1),
training_permission (=false), public_demo_permission (=false), retention_policy
(=retention-policy-v0.1), idempotency_key, workspace_path, cancel_requested,
lease_until, last_error, updated_at`

## ReconstructionResult fields

`result_id, job_id, production_case_id, source_sha256, selected_candidate
(SOURCE|A|B|C), audio_object_ref, reconstruction_version, plan_hash,
engine_version, identity_status, technical_status, created_at`

References the audio object by path; never embeds audio in the database.

## Workspace layout

```text
state/reconstruction_workspace/{job_id}/
  input/      original{suffix}   (owner upload, byte-preserved)
              source.wav         (ffmpeg transcode, sample-rate preserved)
  case/       production_case.json, source_manifest.json,
              era_diagnostic.v0.1.json, golden_record.json, evidence.json
  candidates/ A.wav B.wav C.wav  (rendered via execute_intervention)
  evidence/   (reserved for long-term non-audio records)
  result/     result.json        (final product payload + resource usage)
  tmp/        scratch, always cleaned
```

## Confirmation

No second authority created: job state is a projection; the canonical
ProductionCase is written once per job (never duplicated), evidence is a
canonical `EvidenceArtifact` registry referencing the same files the pipeline
produced.
