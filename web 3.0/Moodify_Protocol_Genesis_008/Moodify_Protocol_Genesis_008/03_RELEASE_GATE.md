# Release Gate
## Genesis v1

### GO

A GO decision requires:

- no CRITICAL findings;
- no unresolved HIGH findings;
- all critical contract tests pass;
- all critical web/API tests pass;
- migrations validated;
- Package 004 root compatibility verified;
- production token config correct;
- human approvals recorded;
- production deployment remains unsigned until operator action;
- public pages contain no fabricated metrics;
- rollback/incident procedures documented.

### CONDITIONAL GO

Allowed only when:

- no CRITICAL findings;
- HIGH findings have explicit human risk acceptance and compensating controls;
- known limitations do not endanger funds or identity integrity.

Every conditional item must have:
- owner;
- due date;
- mitigation;
- monitoring plan.

### NO-GO

Automatic NO-GO if:

- private key leaked;
- admin auth bypass;
- replay vulnerability;
- wrong token contract;
- wrong Merkle root;
- claim mismatch;
- arbitrary drain path;
- unbounded allocation bug;
- participant data leak;
- production deployment config points to unverified contract;
- task-related build/tests fail;
- secret rotation incomplete after exposure.

### Human production approvals

The final release report must list each human-required action:

1. approve production snapshot/root;
2. approve contract parameters;
3. sign production deployment;
4. verify BscScan contract;
5. sign distributor funding;
6. approve treasury/public wallet labels;
7. approve production website release.
