# MHP-051: Runbook & Operator Guide — Production Documentation

**Status**: proposed
**Direction**: 6-Step Plan — S1 (Systemization)
**Depends on**: MHP-050
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- MHP-045 updated ARCHITECTURE.md, CHANGELOG.md, README.md
- But no operator-facing documentation exists for:
  - How to start the API server
  - How to create a job through the Console UI
  - How to read a gate report
  - How to deliver a candidate
  - How to calibrate MRS thresholds
  - Troubleshooting common errors

## Goal

Write a concise operator guide covering the 5 core workflows. Update the Studio OS Alpha runbook with MHP-041→050 additions.

## Non-Goals

- Don't write tutorial docs (wrong phase)
- Don't document internal APIs for external developers

## Acceptance Criteria

- Operator guide covers: job intake, runtime, gate review, delivery, calibration
- Each workflow has CLI and Console UI instructions
- Runbook updated with new endpoints and test counts
- Troubleshooting section covers: server not starting, job stuck, report missing, delivery blocked

## Done Means

An operator with no prior Moodify knowledge can start the server, create a job, process audio, review results, and deliver — using either the CLI or the Console UI.
