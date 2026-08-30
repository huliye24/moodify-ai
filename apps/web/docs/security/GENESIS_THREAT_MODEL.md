# Genesis Threat Model

**Package:** MOOD-GENESIS-008  
**Date:** 2026-08-27  
**Version:** v1.0

---

## Overview

This document describes the threat model for the Moodify Protocol Genesis v1 system.

---

## Threat Actors

### 1. Unauthenticated Internet User

**Capabilities:**
- Access public routes
- Call public APIs
- View transparency data

**Threats:**
- Enumeration attacks
- Rate limit abuse
- Front-running (if mempool visible)

**Mitigations:**
- Rate limiting on sensitive endpoints
- No sensitive data in public APIs
- Static transparency data (no real-time trading data)

### 2. Malicious Genesis Participant

**Capabilities:**
- Registered wallet
- Valid signature
- Knowledge of own allocation

**Threats:**
- Replay attacks (reuse signature)
- Claim manipulation
- Proof tampering

**Mitigations:**
- Nonce single-use enforcement
- Signature binding (domain, chain, terms)
- Merkle proof verification
- Claim uniqueness (participant number)

### 3. Compromised Browser

**Capabilities:**
- Access to user's session
- Modify frontend code
- Intercept wallet communications

**Threats:**
- Address substitution
- Amount manipulation
- Fake transaction confirmation

**Mitigations:**
- Contract verifies msg.sender
- Amount verified in Merkle proof
- Receipt confirmation from chain
- No client-side validation bypass

### 4. Malicious Wallet Extension/Site Clone

**Capabilities:**
- Phishing site
- Fake wallet extension
- Social engineering

**Threats:**
- Steal signatures
- Redirect claims
- Fake approvals

**Mitigations:**
- Official domain verification
- No token approval required
- Clear transaction preview
- BscScan verification links

### 5. Replay Attacker

**Capabilities:**
- Capture valid signatures
- Replay on different chain
- Replay after expiry

**Threats:**
- Reuse valid registration
- Replay claim

**Mitigations:**
- Nonce expiry (600 seconds)
- Chain ID binding (56 only)
- Nonce single-use (DB marked)
- Timestamp validation

### 6. Admin Account Attacker

**Capabilities:**
- Compromise admin credentials
- Access admin endpoints

**Threats:**
- Unauthorized allocation changes
- Data manipulation
- Audit log tampering

**Mitigations:**
- Server-side authorization
- No client-only admin flags
- Audit append-only
- IDOR protection

### 7. Malicious/Buggy Contributor

**Capabilities:**
- Submit contributions
- Review contributions (if authorized)

**Threats:**
- Self-review
- Duplicate submissions
- Spam

**Mitigations:**
- Self-review prevention
- Duplicate submission guards
- Anti-spam measures
- Reputation system

### 8. Malicious API Caller

**Capabilities:**
- Call APIs directly
- Bypass frontend validation
- Script attacks

**Threats:**
- Rate limit evasion
- Data enumeration
- Parameter tampering

**Mitigations:**
- Server-side validation
- Rate limiting
- No sensitive data in public APIs
- Authorization checks

### 9. Erroneous Operator

**Capabilities:**
- Admin access
- Deployment permissions

**Threats:**
- Wrong Merkle root
- Wrong distributor config
- Accidental transfers

**Mitigations:**
- Human approval checkpoints
- Dry-run modes
- Configuration validation
- Reconciliation warnings

### 10. Compromised RPC/Explorer

**Capabilities:**
- Return false data
- Censor transactions
- Delay updates

**Threats:**
- False balance reads
- Transaction censorship
- Stale data

**Mitigations:**
- Source labeling (RPC vs config)
- Stale data detection
- Multiple RPC fallback
- Config fallback for total supply

### 11. Smart Contract Attacker

**Capabilities:**
- Analyze contract bytecode
- Find vulnerabilities
- Exploit logic errors

**Threats:**
- Reentrancy
- Integer overflow
- Access control bypass

**Mitigations:**
- SafeERC20 (reentrancy protection)
- Solidity 0.8.x (overflow protection)
- Immutable root (no admin change)
- Checks-effects-interactions pattern
- No delegatecall
- No selfdestruct

---

## Assets to Protect

### 1. MOOD Treasury

**Value:** High  
**Threats:** Unauthorized transfer, misallocation  
**Controls:**
- Human approval for transfers
- Multi-sig recommended
- Audit trail
- Reconciliation

### 2. Distributor Funds

**Value:** High  
**Threats:** Theft, drain, wrong root  
**Controls:**
- Immutable Merkle root
- Proof verification
- Claim uniqueness
- No arbitrary withdrawal

### 3. Participant Allocation Correctness

**Value:** High  
**Threats:** Wrong amounts, duplicates, exclusions  
**Controls:**
- Deterministic ordering
- Exact arithmetic
- Database constraints
- Reproducible snapshot

### 4. Merkle Root Integrity

**Value:** Critical  
**Threats:** Tampering, wrong root  
**Controls:**
- Immutable in contract
- Human approval required
- Package 004 reproducibility

### 5. Admin Authority

**Value:** High  
**Threats:** Compromise, escalation  
**Controls:**
- Server-side auth
- No client-only flags
- Audit logging

### 6. Participant Wallet Ownership Proofs

**Value:** Medium  
**Threats:** Forgery, replay  
**Controls:**
- EIP-191 signature
- Nonce binding
- Chain binding

### 7. Internal Notes

**Value:** Medium  
**Threats:** Leakage  
**Controls:**
- Not exposed in public APIs
- Admin-only access

### 8. Protocol Reputation/Reward Records

**Value:** Medium  
**Threats:** Tampering, fraud  
**Controls:**
- Append-only ledger
- Review authorization
- Self-review prevention

### 9. Public Transparency Accuracy

**Value:** Medium  
**Threats:** Misinformation, fabrication  
**Controls:**
- Source labeling
- No fabricated metrics
- RPC fallback

---

## Attack Scenarios

### Scenario 1: Replay Attack

**Attack:** Capture valid registration signature, replay on same/different chain  
**Result:** FAIL - Nonce expiry, chain binding, single-use enforcement

### Scenario 2: Claim Amount Manipulation

**Attack:** Modify claim amount in frontend  
**Result:** FAIL - Amount in Merkle leaf, contract verification

### Scenario 3: Double Claim

**Attack:** Claim same allocation twice  
**Result:** FAIL - claimedParticipant mapping prevents

### Scenario 4: Wrong Wallet Claim

**Attack:** Use proof for wallet A with wallet B  
**Result:** FAIL - msg.sender must match leaf account

### Scenario 5: Admin Allocation Tampering

**Attack:** Modify participant allocation  
**Result:** DETECTED - Audit log, DB constraints

### Scenario 6: Contract Drain

**Attack:** Exploit contract to drain funds  
**Result:** FAIL - No arbitrary withdrawal, SafeERC20

### Scenario 7: Fake Transparency Data

**Attack:** Show fabricated metrics  
**Result:** DETECTED - Source labeling, RPC verification

---

## Risk Matrix

| Threat | Likelihood | Impact | Risk |
|--------|-----------|--------|------|
| Replay attack | Low | Medium | Low |
| Claim manipulation | Low | High | Medium |
| Double claim | Low | High | Medium |
| Admin compromise | Low | High | Medium |
| Contract exploit | Low | Critical | Medium |
| RPC compromise | Low | Medium | Low |
| Phishing | Medium | Medium | Medium |

---

## Security Controls Summary

### Prevention
- Input validation
- Signature verification
- Merkle proof verification
- Server-side authorization
- Rate limiting

### Detection
- Audit logging
- Reconciliation
- Anomaly detection
- Source labeling

### Response
- Incident response plan
- Contract pause (not implemented - immutable)
- Emergency recovery (owner only after deadline)

---

## Assumptions

1. BNB Smart Chain is secure
2. OpenZeppelin contracts are secure
3. Human operators follow procedures
4. Participants protect their private keys
5. RPC endpoints are honest majority

---

## Out of Scope

- BNB Smart Chain consensus attacks
- Wallet software vulnerabilities
- Browser zero-days
- Social engineering (beyond documentation)

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
