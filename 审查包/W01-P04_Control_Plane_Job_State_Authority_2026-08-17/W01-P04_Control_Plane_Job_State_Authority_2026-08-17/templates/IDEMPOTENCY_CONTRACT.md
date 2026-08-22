# Idempotency Contract

## Create Job

- key scope:
- key source:
- request fingerprint:
- retention:
- same key + same fingerprint:
- same key + different fingerprint:

## Transition Commands

- command id:
- dedupe window:
- result replay:
- conflict behavior:

## Complete

- worker result identity:
- attempt/fencing validation:
- repeated complete:
- stale complete:

## Failure Report

- repeated failure command:
- event dedupe:

## Storage

- idempotency record location:
- uniqueness constraint:
