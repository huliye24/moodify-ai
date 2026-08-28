# Frontend Specification
## `/airdrop`

### Design principle

This page is a protocol utility, not a speculative trading page.

Preserve current Moodify visual language.

Avoid:
- flashing price widgets;
- countdown hype;
- ROI language;
- "100x" or investment framing;
- fake scarcity.

### Main states

#### 1. Wallet disconnected
CTA:
`Connect Wallet`

Description:
Connect an EVM wallet to check Genesis eligibility.

#### 2. Wrong network
Display:
`Switch to BNB Smart Chain`

Use standard wallet switching.

#### 3. Checking
Show clear eligibility loading state.

#### 4. Not eligible
Display:
- wallet address;
- `Not eligible in this Genesis snapshot`;
- link to Genesis participation/contribution pages if available.

#### 5. Eligible / unclaimed
Display:
- Genesis Participant #
- Allocation: `X MOOD`
- Snapshot ID
- Claim status
- Claim button

#### 6. Wallet confirmation
Before prompting transaction:
- show distributor address;
- amount;
- chain;
- explain no token approval is requested.

#### 7. Pending
Display:
- transaction hash;
- BscScan link;
- pending state.

#### 8. Claimed
Display:
- claimed amount;
- transaction link;
- timestamp if indexed/read;
- immutable success state.

#### 9. Error
Differentiate:
- user rejected transaction;
- insufficient BNB for gas;
- wrong network;
- claim already used;
- invalid/expired campaign;
- contract not funded sufficiently;
- RPC unavailable.

### Data authority

Eligibility/proof:
Package 004 approved artifact.

Claim status:
on-chain contract.

Do not mark a claim successful solely because the frontend submitted a transaction.

Wait for receipt / chain confirmation.

### Contract configuration

Add one config authority for:
- chainId;
- distributor address;
- token address;
- snapshot ID;
- Merkle root;
- deployment block;
- claim deadline if any.

Production distributor address must remain unset until human-signed deployment completes.

Frontend should fail safely if production contract config is missing.

### Privacy

Do not expose private Genesis admin data.

Public proof data may reveal wallet allocations. Document this property.

### Accessibility

- keyboard accessible;
- semantic buttons/status;
- wallet address wrapping;
- progress state not color-only;
- responsive.
