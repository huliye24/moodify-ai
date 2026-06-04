# MHP-036: Studio Back Office

Status: proposed
Direction: studio workflow layer
Depends on: MHP-035 Internal Operator Console UI

## Context

The Operator Console manages production. The Studio Back Office manages the commercial workflow around production: customers, projects, packages, deadlines, and staff notes.

## Goal

Add studio-level order management around Operator Jobs.

## Non-Goals

- Do not implement payment collection.
- Do not build public customer login.
- Do not implement multi-tenant SaaS.

## Product Requirements

Add durable objects:

- `StudioClient`
- `StudioProject`
- `Order`
- `ProcessingPackage`
- `StaffNote`

Orders should link to one or more Operator Jobs.

## Engineering Requirements

- Add JSONL-backed storage for studio records.
- Add API endpoints:

```text
POST /studio/clients
POST /studio/projects
POST /studio/orders
GET  /studio/orders
GET  /studio/orders/{order_id}
POST /studio/orders/{order_id}/jobs
```

- Add UI views:
  - Orders
  - Clients
  - Project detail
  - Linked jobs

## Acceptance Criteria

- An order can be created and linked to jobs.
- A project can show all jobs and delivery status.
- Operator Console can filter by project/order.
- Tests cover order/job linking.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_studio_back_office.py -q
python -m pytest moodify-core-package/tests/test_api_studio.py -q
```

## Done Means

Moodify starts operating like a studio system, not just a runtime tool.
