# Genesis Privacy Review

**Package:** MOOD-GENESIS-008  
**Date:** 2026-08-27  
**Scope:** Packages 001–007

---

## Overview

This document reviews the privacy implications of the Moodify Protocol Genesis v1 system.

**Principle:** Minimize data collection. Protect participant privacy. Document public vs private data.

---

## Data Classification

### Public Data

| Data | Reason | Location |
|------|--------|----------|
| MOOD token address | Required for transactions | lib/mood-token.ts |
| Participant wallet address | Required for claims | genesisParticipants table |
| Participant number | Public identifier | genesisParticipants table |
| Allocation amount | Public claim data | snapshot.json, merkle.json |
| Claim status | Public on-chain | distributor contract |
| Treasury account addresses | Public protocol info | lib/mood-treasury.ts |
| Total supply | Public chain data | BscScan |

### Private Data

| Data | Reason | Protection |
|------|--------|------------|
| Raw signatures | Sensitive auth data | Never logged/stored |
| Nonce values | Replay protection | Hashed only (SHA-256) |
| Internal admin notes | Operational privacy | Admin-only API |
| Contribution evidence URLs | May contain PII | Admin-only review |
| Participant email | Identity | Not collected in Genesis |
| IP addresses | Tracking | Not stored |

### Immutable Protocol Records

These cannot be deleted (blockchain/database):

- Wallet registrations
- Claim transactions
- Contribution submissions
- Reputation events

---

## Component Privacy Analysis

### Package 001: Token Identity

**Data:** Public token metadata  
**Privacy Risk:** None  
**Mitigation:** N/A

---

### Package 002: Registration

**Data Collected:**
- walletAddress (public)
- participantNumber (public)
- signature (verified, not stored raw)
- nonceHash (stored, not raw nonce)

**Privacy Controls:**
- ✅ Raw signature not stored (only verified)
- ✅ Raw nonce not stored (only SHA-256 hash)
- ✅ No email/phone collected
- ✅ No KYC required
- ✅ Wallet address public (required for claims)

**API Privacy:**
```typescript
// Public endpoint returns:
{ participantNumber, address, joinedAt, status }

// Does NOT return:
{ signature, nonce, internalNotes }
```

---

### Package 003: Admin

**Data:**
- Internal notes (private)
- Allocation decisions (audit trail)

**Privacy Controls:**
- ✅ Admin notes not in public API
- ✅ Audit log append-only
- ✅ No raw signatures in logs

---

### Package 004: Distribution

**Data:**
- Participant allocations (public)
- Merkle proofs (public)

**Privacy Controls:**
- ✅ No signatures in artifacts
- ✅ No nonces in artifacts
- ✅ No internal notes in artifacts
- ✅ Only approved participants included

**Artifacts:**
```json
// snapshot.json includes:
{ participantNumber, walletAddress, allocationMood, allocationAtomic }

// Does NOT include:
{ signature, nonce, adminNotes }
```

---

### Package 005: Airdrop

**Data:**
- Claim transactions (public on-chain)
- Proof data (public)

**Privacy Controls:**
- ✅ No private key handling
- ✅ No signature collection
- ✅ Claim data from public Merkle tree
- ✅ Transaction receipt public (blockchain)

**Frontend Privacy:**
- No tracking cookies
- No analytics (by default)
- Wallet connection only for claiming

---

### Package 006: Contribution

**Data:**
- Submission content (reviewed by admin)
- Evidence URLs (may contain PII)
- Reputation scores (public)

**Privacy Controls:**
- ✅ Evidence URLs admin-only
- ✅ Submission content reviewed before public
- ✅ No real names required
- ✅ Reputation public (protocol decision)

---

### Package 007: Transparency

**Data:**
- Treasury balances (public)
- Genesis aggregates (public)

**Privacy Controls:**
- ✅ No individual transaction details
- ✅ Aggregated data only
- ✅ No fabricated metrics
- ✅ Source labeling

**API Privacy:**
```json
// /api/protocol/transparency returns:
{ aggregatedStats, methodology }

// Does NOT return:
{ individualWallets, internalNotes, signatures }
```

---

## Data Retention

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| Wallet registrations | Permanent | Protocol record |
| Claim transactions | Permanent | Blockchain immutable |
| Contribution submissions | Permanent | Protocol record |
| Reputation events | Permanent | Protocol record |
| Nonce hashes | 30 days | Replay protection |
| Admin audit logs | Permanent | Accountability |
| RPC logs | 7 days | Debugging |

---

## GDPR/CCPA Considerations

**Not Applicable:**
- No personal data collection (email, name, address)
- Only wallet addresses (pseudonymous)
- No tracking/analytics
- No cookies

**If Applicable (future):**
- Right to deletion: Limited (blockchain immutable)
- Right to access: All data is public
- Data portability: Wallet addresses exportable

---

## Privacy Risks & Mitigations

### Risk 1: Wallet Address Linking

**Risk:** Wallet addresses could be linked to real identity  
**Mitigation:**
- No KYC required
- No email/phone collected
- Wallet address is pseudonymous

### Risk 2: Evidence URL Leakage

**Risk:** Contribution evidence may contain PII  
**Mitigation:**
- Evidence URLs admin-only
- Review before any public display
- Sanitization guidelines

### Risk 3: Signature Replay

**Risk:** Signatures could be replayed  
**Mitigation:**
- Nonce single-use
- Chain binding
- Expiry enforcement

### Risk 4: Admin Note Exposure

**Risk:** Internal notes could leak  
**Mitigation:**
- Admin-only API endpoints
- No notes in public responses
- Access logging

---

## Public API Privacy

All public APIs are designed to return only non-sensitive data:

| Endpoint | Public Data | Private Data Excluded |
|----------|-------------|----------------------|
| /api/genesis/me | participantNumber, status | signature, nonce |
| /api/airdrop/eligibility | amount, proof | internal notes |
| /api/protocol/transparency | aggregates | individual data |
| /api/contribution/tasks | public tasks | reviewer notes |

---

## Privacy Checklist

- [x] No unnecessary data collection
- [x] Raw signatures not stored
- [x] Raw nonces not stored
- [x] No email/phone required
- [x] No KYC
- [x] No tracking cookies
- [x] Admin notes private
- [x] Evidence URLs private
- [x] Public APIs sanitized
- [x] Data retention documented

---

## Recommendations

### Pre-Launch
1. Review all public API responses for data leakage
2. Verify admin endpoints require authentication
3. Confirm evidence URL access controls

### Post-Launch
1. Monitor for unexpected data exposure
2. Review access logs regularly
3. Document any privacy incidents

---

## Sign-off

**Privacy Review:** COMPLETE  
**Data Minimization:** PASS  
**Public API Safety:** PASS  
**Release Recommendation:** **GO**

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
