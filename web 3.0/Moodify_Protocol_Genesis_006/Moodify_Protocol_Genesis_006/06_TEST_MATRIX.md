# Test Matrix
## Contribution Network

| ID | Scenario | Expected |
|---|---|---|
| C-001 | Public views active tasks | active only |
| C-002 | Public views draft task | hidden/denied |
| C-003 | Registered participant submits | success |
| C-004 | Unregistered wallet submits | denied |
| C-005 | Invalid task | denied |
| C-006 | Paused task submission | denied |
| C-007 | Deadline passed | denied if deadline enforced |
| C-008 | Duplicate submission disallowed task | denied |
| C-009 | submitted → under_review | success |
| C-010 | under_review → changes_requested | success |
| C-011 | changes_requested → submitted | success |
| C-012 | under_review → approved | success |
| C-013 | under_review → rejected | success |
| C-014 | invalid transition | denied |
| C-015 | unauthorized reviewer | denied |
| C-016 | self-review | denied where identity linked |
| C-017 | approval points = 10 | reputation event +10 |
| C-018 | approval reward = 100 MOOD | pending reward exact |
| C-019 | reward with 18 decimals | exact |
| C-020 | reward >18 decimals | rejected |
| C-021 | negative reward | rejected |
| C-022 | reward uses float path | test must prevent |
| C-023 | approval duplicated | second reward not created |
| C-024 | max approvals reached | further approval denied |
| C-025 | cancelled reward | append audit, no deletion |
| C-026 | reputation rollback | negative event appended |
| C-027 | cached reputation | equals event sum |
| C-028 | Genesis allocation before approval | unchanged |
| C-029 | Genesis allocation after contribution approval | unchanged |
| C-030 | reward export | deterministic |
| C-031 | reward export notes/signatures | absent |
| C-032 | user My Contributions | only their records |
| C-033 | another participant submissions | inaccessible if private |
| C-034 | evidence URL malformed | validation error |
| C-035 | GitHub PR URL valid | accepted as evidence |
| C-036 | trading-volume task category | not supported |
| C-037 | buy-to-earn reward | not supported |
| C-038 | task archive | no new submissions |
| C-039 | 1000 submissions | review queue remains usable |
| C-040 | migration | existing Genesis data preserved |

### Manual end-to-end test

1. Admin creates a small test task.
2. Admin activates task.
3. Genesis Participant opens `/contribute`.
4. Participant submits evidence.
5. Admin opens review queue.
6. Admin requests changes.
7. Participant resubmits.
8. Admin approves with points + pending MOOD.
9. Participant sees Reputation update.
10. Participant sees pending MOOD allocation.
11. Run pending reward export.
12. Confirm no chain transaction occurred.
