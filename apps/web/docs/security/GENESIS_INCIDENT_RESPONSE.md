# Genesis Incident Response

**Package:** MOOD-GENESIS-008  
**Date:** 2026-08-27  
**Version:** v1.0

---

## Overview

This document provides incident response procedures for the Moodify Protocol Genesis v1 system.

**Emergency Contact:** [To be configured]

---

## Incident Severity Levels

| Level | Description | Examples | Response Time |
|-------|-------------|----------|---------------|
| P0 | Critical | Contract vulnerability, fund loss | Immediate |
| P1 | High | Admin compromise, data breach | 1 hour |
| P2 | Medium | RPC outage, claim failures | 4 hours |
| P3 | Low | UI bugs, stale data | 24 hours |

---

## Response Procedures

### P0: Critical Incidents

#### Contract Vulnerability Discovered

**Detect:**
- Anomalous claim patterns
- Unexpected contract behavior
- Security alert from monitoring

**Contain:**
1. Immediately assess if funds at risk
2. If distributor vulnerable:
   - Cannot pause (immutable)
   - Cannot upgrade (no proxy)
   - Only recovery after deadline (if set)
3. Document vulnerability details

**Communicate:**
1. Alert core team
2. Prepare public disclosure
3. Coordinate with security researchers

**Recover:**
1. Deploy new distributor (if applicable)
2. Update frontend to new contract
3. Migrate unclaimed allocations

**Preserve:**
- Transaction hashes
- Vulnerability details
- Timeline

---

#### Wrong Merkle Root Deployed

**Detect:**
- Claims failing for valid participants
- Root mismatch with approved snapshot

**Contain:**
1. Stop all claim attempts
2. Assess impact (how many affected)

**Communicate:**
1. Notify participants
2. Explain situation

**Recover:**
1. Deploy new distributor with correct root
2. Update frontend config
3. Fund new distributor
4. Test claims

**Preserve:**
- Wrong root transaction
- Correct root approval
- Deployment timeline

---

#### Distributor Underfunded

**Detect:**
- Claim reverts with insufficient balance
- Distributor balance < total allocation

**Contain:**
1. Assess shortfall
2. Calculate required funding

**Communicate:**
1. Notify affected participants
2. Explain delay

**Recover:**
1. Transfer additional MOOD to distributor
2. Verify balance
3. Resume claims

**Preserve:**
- Funding transaction
- Shortfall calculation

---

#### Admin Credential Compromise

**Detect:**
- Unauthorized allocation changes
- Suspicious admin activity

**Contain:**
1. Revoke compromised credentials
2. Audit all recent admin actions
3. Check for data tampering

**Communicate:**
1. Notify team
2. Assess participant impact

**Recover:**
1. Reset admin credentials
2. Verify allocation integrity
3. Re-snapshot if necessary

**Preserve:**
- Audit logs
- Access logs
- Timeline

---

### P1: High Incidents

#### Frontend Config Wrong

**Detect:**
- Wrong distributor address
- Wrong chain ID

**Contain:**
1. Identify wrong config
2. Assess if any transactions sent

**Recover:**
1. Update frontend config
2. Redeploy if necessary
3. Verify claims work

---

#### DB Allocation Corruption

**Detect:**
- Allocation totals mismatch
- Duplicate participant numbers

**Contain:**
1. Stop allocation changes
2. Assess extent of corruption

**Recover:**
1. Restore from backup
2. Re-run snapshot generation
3. Verify integrity

---

#### Leaked Private Key

**Detect:**
- Unauthorized transactions
- Suspicious fund movements

**Contain:**
1. Immediately move funds if possible
2. Revoke compromised key

**Communicate:**
1. Notify team
2. Assess exposure

**Recover:**
1. Generate new key
2. Update all systems
3. Rotate any exposed credentials

**Preserve:**
- Leak source
- Exposure timeline

---

### P2: Medium Incidents

#### RPC Outage

**Detect:**
- Transparency page shows stale data
- Balance reads failing

**Contain:**
1. Switch to fallback RPC
2. Enable cached data

**Recover:**
1. Restore RPC connection
2. Refresh all data

---

#### BscScan Metadata Mismatch

**Detect:**
- Contract verification shows different code
- Source mismatch

**Contain:**
1. Verify actual deployed code
2. Check for unauthorized changes

**Recover:**
1. Re-verify contract if needed
2. Document discrepancy

---

#### Malicious Contribution Spam

**Detect:**
- High volume of spam submissions
- Evidence URL abuse

**Contain:**
1. Enable rate limiting
2. Block spam sources

**Recover:**
1. Clean spam submissions
2. Review legitimate submissions

---

### P3: Low Incidents

#### UI Bug

**Detect:**
- Display issues
- Wrong data shown

**Recover:**
1. Fix in next deployment
2. Document workaround

---

## Incident Response Team

| Role | Responsibility | Contact |
|------|----------------|---------|
| Incident Commander | Overall coordination | [TBD] |
| Security Lead | Vulnerability assessment | [TBD] |
| Dev Lead | Technical fixes | [TBD] |
| Communications | Public updates | [TBD] |

---

## Communication Templates

### Public Disclosure (Critical)

```
SECURITY ADVISORY: Moodify Protocol

We have identified a [brief description] in the Genesis system.

Impact: [affected users/components]
Status: [contained/investigating/fixed]
Action Required: [user actions]

We will provide updates at [communication channel].

Timeline:
- [Time]: Issue detected
- [Time]: Investigation began
- [Time]: Fix deployed

Contact: security@moodify.example
```

### Participant Notification (High)

```
Important Update: Genesis Claim

We are experiencing [issue]. Your claim may be delayed.

Expected resolution: [timeframe]
No action required from you.

Updates: [link]
```

---

## Monitoring & Detection

### On-Chain Monitoring

- Claim event frequency
- Distributor balance
- Failed transaction rate
- Unusual claim patterns

### Off-Chain Monitoring

- API error rates
- RPC response times
- Database integrity
- Frontend errors

### Alerts

| Condition | Severity | Channel |
|-------------|----------|---------|
| Distributor balance < threshold | P0 | Email, SMS |
| Failed claim rate > 10% | P1 | Email |
| RPC down > 5 min | P2 | Email |
| API errors > 100/min | P2 | Slack |

---

## Recovery Checklists

### Contract Vulnerability

- [ ] Assess fund risk
- [ ] Document vulnerability
- [ ] Notify team
- [ ] Prepare fix
- [ ] Deploy new contract
- [ ] Update frontend
- [ ] Test thoroughly
- [ ] Public disclosure
- [ ] Postmortem

### Wrong Root

- [ ] Identify correct root
- [ ] Prepare new deployment
- [ ] Deploy new distributor
- [ ] Update frontend config
- [ ] Fund new distributor
- [ ] Test claims
- [ ] Notify participants
- [ ] Document incident

### Admin Compromise

- [ ] Revoke credentials
- [ ] Audit all actions
- [ ] Check data integrity
- [ ] Reset credentials
- [ ] Verify allocations
- [ ] Update team
- [ ] Document incident

---

## Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date:** [Date]
**Severity:** [P0/P1/P2/P3]
**Duration:** [Time]

## Summary
[Brief description]

## Timeline
- [Time]: Issue detected
- [Time]: Response began
- [Time]: Contained
- [Time]: Resolved

## Root Cause
[What happened and why]

## Impact
- [Affected users/systems]
- [Data loss/financial impact]

## Resolution
[How it was fixed]

## Lessons Learned
- [What went well]
- [What could be improved]

## Action Items
- [ ] [Task] - Owner - Due date

## Prevention
[How to prevent recurrence]
```

---

## Contact Information

| Role | Name | Email | Phone |
|------|------|-------|-------|
| Incident Commander | [TBD] | [TBD] | [TBD] |
| Security Lead | [TBD] | [TBD] | [TBD] |
| Dev Lead | [TBD] | [TBD] | [TBD] |

---

## External Resources

- BscScan: https://bscscan.com
- PancakeSwap: https://pancakeswap.finance
- OpenZeppelin: https://docs.openzeppelin.com

---

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
