# Moodify API

**Status:** Experimental repository API facade. This documentation is an integration architecture, not a public service-level commitment or a claim of deployed cloud capacity.

Moodify API provides auditory-intelligence capabilities for applications through a versioned FastAPI boundary. It is intended as a future integration foundation for AI music platforms, music companies, creator tools, and audio applications, subject to validation, security, operations, and product-boundary decisions.

## Endpoints

All new facade endpoints are scoped under `/api/v1/intelligence` to avoid changing existing `/api/v1/auditory` behavior.

### Audio Analysis API

`POST /api/v1/intelligence/analyze`

**Input:** multipart `audio` file and optional JSON-string `metadata` form field.

**Output:** `duration`, detected `format`, and acoustic `features` from the existing v0.1 analysis engine.

### Audio Evaluation API

`POST /api/v1/intelligence/evaluate`

**Input:** multipart `audio`, optional `metadata`, and optional `normalized_features` JSON string matching the experimental MRS feature contract.

**Output:** `score` and `metrics`. Without explicitly supplied normalized MRS features, the response returns `score: null` and `status: FEATURES_REQUIRED`; raw acoustic values are not represented as a human listening score.

### Audio Processing API

`POST /api/v1/intelligence/process`

**Input:** multipart `audio` file.

**Output:** `501 NOT_IMPLEMENTED`. The route reserves a future contract and does not expose or alter an existing processing pipeline.

## Architecture

```text
FastAPI route
    ↓
AudioService
    ↓
Existing analysis engine / experimental MRS module
    ↓
Typed Pydantic response
```

Routes manage HTTP validation and status codes. `AudioService` owns temporary upload handling and core-module adaptation. Existing core algorithms remain independent of FastAPI and can later be replaced behind this boundary by model, GPU-worker, or remote-execution adapters.

## Operational Boundary

- The API has no new authentication, tenant isolation, rate limiting, object storage, or background execution in this task.
- It accepts bounded local uploads according to `MOODIFY_MAX_UPLOAD_BYTES`.
- It does not claim a deployed public endpoint, cloud AI inference, or production MRS authority.
- The current public product remains Moodify Music / Player; this is an internal technical integration layer.
