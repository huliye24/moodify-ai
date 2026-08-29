# Accounting Model
## Transparency & Treasury v1

### Accounting layers

Moodify must keep these concepts separate:

#### 1. On-chain balance

What `MOOD.balanceOf(address)` currently reports.

This is objective chain state.

#### 2. Allocation

An off-chain approved intention or entitlement.

Examples:
- Genesis allocation;
- pending contribution reward.

Allocation does not imply the token has moved.

#### 3. Distribution

MOOD has actually been transferred into:
- participant wallet;
- distributor;
- another approved protocol account.

#### 4. Claim

A participant successfully claimed through the Package 005 distributor.

#### 5. Treasury reserve

MOOD held by a wallet/contract explicitly approved and publicly classified as protocol treasury/reserve.

#### 6. Circulating supply

Requires an approved methodology.

Do not infer casually.

### Recommended public labels

For each metric identify `sourceType`:

```text
onchain
database
snapshot
configured
derived
```

And `confidence` or `status` where useful:

```text
verified
approved
draft
unavailable
```

### Genesis accounting

Recommended:

```text
registeredParticipants
allocatedParticipants
totalAllocatedMood
snapshotTotalMood
distributorFundedMood
claimedParticipants
claimedMood
unclaimedMood
```

Do not show `claimedMood` based only on DB status if contract exists.
Prefer chain events/state.

### Contribution accounting

Recommended:

```text
pendingRewardMood
includedInSnapshotMood
distributedRewardMood
```

Do not add pending rewards to circulating supply.

### Treasury percentage

For a configured account:

```text
balancePctOfTotal =
balanceAtomic / totalSupplyAtomic
```

Use exact integer arithmetic then format for display.

### Reconciliation warning examples

- configured account missing from RPC;
- chain ID mismatch;
- token contract mismatch;
- distributor config points to zero address;
- DB says distributed but no chain evidence;
- snapshot total differs from distributor funding target;
- duplicate treasury address labels.

These are warnings, not silent corrections.
