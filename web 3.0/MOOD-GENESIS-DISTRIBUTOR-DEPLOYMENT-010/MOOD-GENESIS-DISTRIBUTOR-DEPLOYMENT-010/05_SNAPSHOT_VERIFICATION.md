# Genesis Snapshot Verification

Required report:

```text
Snapshot path:
Snapshot SHA-256:
Generator path:
Generator commit:
Generation command:
Participant count:
Total MOOD allocation:
Token decimals:
Merkle root run #1:
Merkle root run #2:
Roots identical: YES/NO
```

## Validation

- valid EVM addresses;
- duplicate addresses detected;
- no negative allocations;
- no floating-point base-unit arithmetic;
- exact reproducible total;
- demo/mock rows excluded;
- representative proofs verified where tooling exists.

After approval, any change to the snapshot/root/count/total invalidates the approval.
