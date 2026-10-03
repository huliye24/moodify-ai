/**
 * MOOD-SECURITY-022: Security Model
 *
 * Canonical security status payload for /security page and /network integration.
 *
 * HONEST defaults reflect the v1 state:
 *   - Audit not completed
 *   - Single-operator custody
 *   - Some staging gates open
 *
 * No private keys, no secrets, no internal hostnames.
 */

export type SecurityOverallStatus = "ok" | "open-findings" | "unavailable";

export type GateStatus = "passed" | "open" | "blocked" | "not-applicable";

export interface StagingGateStatus {
  id: string;
  name: string;
  status: GateStatus;
  evidence?: string;
}

export interface PublicTrustClaim {
  id: string;
  claim: string;
  evidenceRef: string;
  scope: string;
  status: "verified" | "partial" | "open";
  lastVerified: string;
}

export interface SecurityFinding {
  id: string;
  severity: "P0" | "P1" | "P2" | "P3" | "Info";
  title: string;
  status: "open" | "mitigated" | "deferred" | "closed";
  affected: string[];
  evidenceRef?: string;
}

export interface SecurityStatusPayload {
  schema: "moodify-security-status-v1";
  generatedAt: string;
  overallStatus: SecurityOverallStatus;
  summary: {
    auditCompleted: boolean;
    custodianModel: "single-operator" | "multi-sig" | "unknown";
    treasuryActive: boolean;
    autoPayoutEnabled: boolean;
    aiSignerEnabled: boolean;
    tokenTaxEnabled: boolean;
  };
  stagingGate: {
    ready: boolean;
    blockers: string[];
    openGates: string[];
    gates: StagingGateStatus[];
  };
  trustClaims: PublicTrustClaim[];
  findings: SecurityFinding[];
  channels: {
    securityContact: string;
    disclosurePolicy: string;
  };
  incidentResponse: string;
}

// ────────────────────────────────────────────────────────────────────────────
// Defaults (v1 — HONEST state)
// ────────────────────────────────────────────────────────────────────────────

export const DEFAULT_STAGING_GATES: StagingGateStatus[] = [
  {
    id: "SG0",
    name: "No P0 open",
    status: "passed",
    evidence: "docs/mood/security/022_FINDINGS.md",
  },
  {
    id: "SG1",
    name: "No internet-exploitable P1",
    status: "open",
    evidence: "F-005 (rate limit), F-006 (markdown), F-007 (CSP)",
  },
  {
    id: "SG2",
    name: "Auth/session controls verified",
    status: "open",
    evidence: "TBD code audit by 023",
  },
  {
    id: "SG3",
    name: "Admin APIs fail closed",
    status: "open",
    evidence: "TBD code audit by 023",
  },
  {
    id: "SG4",
    name: "No secrets in repository / public bundle",
    status: "passed",
    evidence: "docs/mood/security/022_SECRET_INVENTORY.md",
  },
  {
    id: "SG5",
    name: "Rate limiting on mutations",
    status: "open",
    evidence: "Not yet implemented",
  },
  {
    id: "SG6",
    name: "Security headers baseline",
    status: "open",
    evidence: "Not yet implemented (deferred to 023)",
  },
  {
    id: "SG7",
    name: "Public serializers reviewed",
    status: "open",
    evidence: "F-008 review pending",
  },
  {
    id: "SG8",
    name: "Incident response published",
    status: "passed",
    evidence: "docs/mood/security/022_INCIDENT_RESPONSE.md",
  },
  {
    id: "SG9",
    name: "Security page honest",
    status: "passed",
    evidence: "apps/web/app/security/page.tsx",
  },
  {
    id: "SG10",
    name: "Treasury / Token writes disabled",
    status: "passed",
    evidence: "docs/mood/treasury/021_FINAL_REPORT.md",
  },
];

export const DEFAULT_TRUST_CLAIMS: PublicTrustClaim[] = [
  {
    id: "TC-001",
    claim: "Treasury is not yet activated; no real protocol-controlled funds exist.",
    evidenceRef: "docs/mood/treasury/021_FINAL_REPORT.md",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-002",
    claim: "AI Agents cannot move Treasury funds or sign on-chain transactions.",
    evidenceRef: "docs/mood/security/022_PERMISSION_MATRIX.md",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-003",
    claim: "Passport login uses wallet signature only; no token transfer or approval.",
    evidenceRef: "apps/web/lib/genesis-message.ts",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-004",
    claim: "MOOD Governance is maintainer-reviewed; not token-weighted.",
    evidenceRef: "docs/mood/governance/020_FINAL_REPORT.md",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-005",
    claim: "Repository contains no private keys, seeds, mnemonics, or signing material.",
    evidenceRef: "docs/mood/security/022_SECRET_INVENTORY.md",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-006",
    claim: "Public API errors are sanitized; no stack trace or secret exposed.",
    evidenceRef: "docs/mood/security/022_FINDINGS.md (F-011)",
    scope: "Public",
    status: "partial",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-007",
    claim: "Future token economics are launch-gated; NOT active in v1.",
    evidenceRef: "apps/web/lib/treasury/model.ts",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-008",
    claim: "Independent third-party security audit: Not completed.",
    evidenceRef: "/security page",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-009",
    claim: "v1 Treasury custody is single-operator; multi-sig requires an accepted MIP.",
    evidenceRef: "docs/mood/treasury/021_TREASURY_POLICY.md",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
  {
    id: "TC-010",
    claim: "No AI-driven auto-payout, LP, or holder reward distribution.",
    evidenceRef: "docs/mood/security/022_FINDINGS.md (F-009, F-010)",
    scope: "Public",
    status: "verified",
    lastVerified: "2026-08-30",
  },
];

export const DEFAULT_FINDINGS: SecurityFinding[] = [
  {
    id: "F-001",
    severity: "P0",
    title: "Single-Maintainer Custody (Treasury)",
    status: "open",
    affected: ["021"],
    evidenceRef: "docs/mood/treasury/021_HANDOFF_022.md",
  },
  {
    id: "F-005",
    severity: "P1",
    title: "No rate limiting on public mutation endpoints",
    status: "open",
    affected: ["cross"],
  },
  {
    id: "F-006",
    severity: "P1",
    title: "Markdown rendering without strict sanitization",
    status: "open",
    affected: ["016", "020"],
  },
  {
    id: "F-007",
    severity: "P1",
    title: "CSP not configured",
    status: "open",
    affected: ["web"],
  },
  {
    id: "F-008",
    severity: "P1",
    title: "Node public API may expose internal hostname",
    status: "open",
    affected: ["019"],
  },
  {
    id: "F-009",
    severity: "P0",
    title: "Agent could inherit transfer authority if mis-configured",
    status: "mitigated",
    affected: ["018"],
    evidenceRef: "No transfer/sign/approve tools in agent capabilities",
  },
  {
    id: "F-010",
    severity: "Info",
    title: "MIP author cannot self-accept (hard rule)",
    status: "mitigated",
    affected: ["020"],
  },
  {
    id: "F-011",
    severity: "P2",
    title: "Public API errors may include stack trace (partial)",
    status: "open",
    affected: ["cross"],
  },
  {
    id: "F-013",
    severity: "Info",
    title: "No third-party audit completed",
    status: "open",
    affected: ["cross"],
  },
];

// ────────────────────────────────────────────────────────────────────────────
// Payload builder
// ────────────────────────────────────────────────────────────────────────────

export function buildSecurityStatusPayload(): SecurityStatusPayload {
  const openGates = DEFAULT_STAGING_GATES
    .filter((g) => g.status !== "passed")
    .map((g) => g.id);

  const blockers = DEFAULT_STAGING_GATES
    .filter((g) => g.status === "blocked")
    .map((g) => g.id);

  return {
    schema: "moodify-security-status-v1",
    generatedAt: new Date().toISOString(),
    overallStatus: blockers.length > 0 ? "unavailable" : "open-findings",
    summary: {
      auditCompleted: false,
      custodianModel: "single-operator",
      treasuryActive: false,
      autoPayoutEnabled: false,
      aiSignerEnabled: false,
      tokenTaxEnabled: false,
    },
    stagingGate: {
      ready: blockers.length === 0 && openGates.length === 0,
      blockers,
      openGates,
      gates: DEFAULT_STAGING_GATES,
    },
    trustClaims: DEFAULT_TRUST_CLAIMS,
    findings: DEFAULT_FINDINGS,
    channels: {
      securityContact: "Security contact channel pending",
      disclosurePolicy: "docs/mood/security/022_DISCLOSURE_POLICY.md",
    },
    incidentResponse: "docs/mood/security/022_INCIDENT_RESPONSE.md",
  };
}
