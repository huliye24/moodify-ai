# External Service Adapter Contract

## General Interface

```text
execute(input_objects, request, context) -> AdapterResult
```

## AdapterResult

- provider
- capability
- provider_job_id
- provider_version/model
- request fingerprint
- input refs
- output refs
- duration
- usage/cost metadata if available
- evidence
- safe diagnostics

## Failure Mapping

- 429 → EXTERNAL_API_RATE_LIMIT
- timeout/5xx → EXTERNAL_API_TRANSIENT
- invalid request/provider rejection → EXTERNAL_API_PERMANENT unless proven otherwise

## Secret Rules

- no key in logs
- no key in manifest
- no signed URL query in long-lived logs
- config refers to secret source, not secret value

## Current Providers

Fill only from verified project reality:

- stem provider:
- post-processing provider:
- other:
