# Object Key Convention — Decision Template

## Goals

- stable
- traceable
- non-secret
- cross-platform
- lifecycle-friendly
- not dependent on original filename
- not used as sole business identity

## Candidate

```text
moodify/
  tracks/{track_id}/
    source/{source_object_id}.{ext}
    jobs/{job_id}/
      stems/{artifact_id}/{role}.{ext}
      analysis/{artifact_id}.{ext}
      intermediate/{artifact_id}.{ext}
      renders/{artifact_id}.{ext}
      evidence/{artifact_id}.{ext}
```

## Final Decision

- Bucket:
- Root prefix:
- Track prefix:
- Job prefix:
- Source convention:
- Stem convention:
- Analysis convention:
- Intermediate convention:
- Render convention:
- Evidence convention:
- Temporary convention:
- Forbidden characters:
- Original filename handling:
- Collision behavior:
- Versioning behavior:
- Lifecycle class mapping:

## Examples

Provide synthetic examples only.
Do not use private user filenames.
