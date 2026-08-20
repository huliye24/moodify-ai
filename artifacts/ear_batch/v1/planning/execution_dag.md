# Execution DAG

The graph is acyclic and ordered by contract dependency.

- `WI-001` <- root
- `WI-002` <- WI-001
- `WI-003` <- WI-001, WI-002
- `WI-004` <- WI-002, WI-003
- `WI-005` <- WI-001, WI-002, WI-003, WI-004
- `WI-006` <- WI-001
- `WI-007` <- WI-002, WI-003
- `WI-008` <- WI-007
- `WI-009` <- WI-002, WI-003, WI-007
- `WI-010` <- WI-003, WI-004
- `WI-011` <- WI-004, WI-010
- `WI-012` <- WI-005
