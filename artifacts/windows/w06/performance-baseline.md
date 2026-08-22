# Performance Baseline

Environment: Windows, Node/Vitest, synthetic metadata, 2026-08-21. The focused W06 suite completed all nine tests—including 100, 1,000 and 5,000 Track search/sort projections—in 247 ms total test time (2.21 s runner wall time).

| Dataset | Result |
|---:|---|
| 100 | PASS; synchronous search + artist sort |
| 1,000 | PASS; synchronous search + artist sort |
| 5,000 | PASS; synchronous search + artist sort |

No virtualization or index was introduced: evidence does not justify a second cache/index authority. Favorite toggle is O(n) over relations and immediately persisted; views use bounded React state with no event-list duplication.
