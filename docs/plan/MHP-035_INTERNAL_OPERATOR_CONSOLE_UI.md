# MHP-035: Internal Operator Console UI

Status: proposed
Direction: first real control surface
Depends on: MHP-034 Delivery Records

## Context

The backend now has jobs, runtime evidence, reports, gates, and delivery records. MHP-035 builds the first internal UI around these primitives.

## Goal

Build the first usable internal Operator Console.

## Non-Goals

- Do not build a landing page.
- Do not optimize for public consumers.
- Do not hide industrial status behind simplified app language.
- Do not create a decorative hero or marketing dashboard.

## Product Requirements

First screen:

```text
Queue / Jobs table
  -> selected Job detail
  -> candidate list
  -> score and gate panel
  -> report links
  -> delivery action
```

Required views:

- Queue
- Job Detail
- Reports
- Delivery
- Craft Library placeholder

Required states:

- empty queue
- waiting
- running
- gate review
- reprocess
- failed
- delivered

## UI Direction

- Dense, operational, work-focused layout.
- No consumer-app upload toy.
- Use compact tables, status badges, tabs, and right-side detail rail.
- Show reports and gate decisions as product information.

## Engineering Requirements

- Use the Operator API from MHP-031 to MHP-034.
- Use mock data only if the API is unavailable in local dev.
- Add a route or screen for:

```text
/operator
/operator/jobs/{job_id}
```

## Acceptance Criteria

- Operator can create a job from UI.
- Operator can list jobs.
- Operator can open a job detail.
- Operator can see candidate versions, scores, and gates.
- Operator can generate or open a report bundle.
- Operator can create a delivery record.

## Test Plan

- Unit tests for UI data adapters.
- API smoke against local dev server.
- Playwright screenshot for desktop and mobile widths if a web UI is used.

## Done Means

Moodify has stopped looking like an app and starts behaving like a control room.
