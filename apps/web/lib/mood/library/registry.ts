// MOOD LIBRARY 014 — Document registry
// Authority: docs/mood/library/014_DOCUMENT_INVENTORY.md

import type {
  LibraryDocument,
  LibraryFilter,
  LibraryCategoryGroup,
} from "./types";

// sourceSha is the HEAD commit at registration time.
// All SHA-256 values are computed over the registered file content
// at the same commit. Re-running the hash verification script
// (scripts/library_hash_check.mjs) will re-verify these values.
export const REGISTRATION_COMMIT = "97c9106859b643f83bb21720afa64a95f95258b5";
export const REGISTRATION_DATE = "2026-08-30";

// 014 ships the following registry. Source files at registration are
// those present on origin/main as of REGISTRATION_COMMIT.
//
// docs/mood/* were authored by 011 / 013 (prior commits in same lineage).
// docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md and docs/canon/CURRENT_CANON.md
// were authored under the existing Public Form canon lineage.

// ============================================================
// FOUNDATION
// ============================================================

const MOOD_CANON: LibraryDocument = {
  slug: "mood-canon",
  title: "MOOD Canon",
  category: "foundation",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "MOOD = WORLD + PROTOCOL + PORTAL. Token is not the product, protocol, or world. " +
    "Single authoritative canon for MOOD-level identity.",
  sourcePath: "docs/mood/CURRENT_CANON.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/CURRENT_CANON.md",
  onlineUrl: "/library/mood-canon",
  sha256: "6509b960cd0cfe5c64918f6a4d7662e687ba3625544961f0fa5321052061fb1b",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_ARCHITECTURE: LibraryDocument = {
  slug: "mood-architecture",
  title: "MOOD System Architecture",
  category: "foundation",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "Three-layer boundary: WORLD / PROTOCOL / PORTAL plus future MOOD Token layer. " +
    "on-chain / off-chain boundaries. Passport / Reputation off-chain by default.",
  sourcePath: "docs/mood/SYSTEM_ARCHITECTURE.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/SYSTEM_ARCHITECTURE.md",
  onlineUrl: "/library/mood-architecture",
  sha256: "0e9de7b203bc250fd6947688637b0589623c176f391f775b4706bcbe9ea6df64",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_PRODUCT_RELATIONSHIP: LibraryDocument = {
  slug: "mood-product-relationship",
  title: "MOOD Product Relationship",
  category: "foundation",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "MOOD vs Moodify Music/Player vs crestwavecoin.com. Moodify is Genesis Application, " +
    "not the world. crestwavecoin.com is WORLD Home (PLANNED).",
  sourcePath: "docs/mood/PRODUCT_RELATIONSHIP.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/PRODUCT_RELATIONSHIP.md",
  onlineUrl: "/library/mood-product-relationship",
  sha256: "bed3e0ce7821dbebea2fa75be6e74f74d5d797e4c08eacc5162e6aef29cd5c80",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_LAUNCH_GATE: LibraryDocument = {
  slug: "mood-launch-gate",
  title: "MOOD Token Launch Gate (G0–G11)",
  category: "governance",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "Token activation BLOCKED until G0..G11 ALL PASS. G0 advanced by 011; G1..G11 NOT_STARTED. " +
    "025 MOOD Token Activation must not begin until all gates PASS.",
  sourcePath: "docs/mood/TOKEN_LAUNCH_GATE.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/TOKEN_LAUNCH_GATE.md",
  onlineUrl: "/library/mood-launch-gate",
  sha256: "1bce11cf7ee2b07ca674fbe8442d81d8b8bb3cf8d07299635d33976699a136c8",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_ASSET_CLASSIFICATION: LibraryDocument = {
  slug: "mood-asset-classification",
  title: "MOOD Asset Classification",
  category: "governance",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "KEEP / KEEP BUT DARK / FREEZE / SEPARATE. Genesis v1.0 and 009 cloud worker " +
    "assets are FREEZE. Token-adjacent UI/services stay dark until G0..G11 PASS.",
  sourcePath: "docs/mood/ASSET_CLASSIFICATION.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/ASSET_CLASSIFICATION.md",
  onlineUrl: "/library/mood-asset-classification",
  sha256: "928beffe91b5ffbca26240f14fdd5db49ea2a41c97d770009d21fbcee7b23062",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_ROADMAP: LibraryDocument = {
  slug: "mood-roadmap",
  title: "MOOD Build Roadmap (011–025)",
  category: "governance",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "011 → 025 roadmap. Each package advances one or more G0..G11. 025 BLOCKED " +
    "until G0..G11 ALL PASS.",
  sourcePath: "docs/mood/SEPTEMBER_BUILD_ROADMAP.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/SEPTEMBER_BUILD_ROADMAP.md",
  onlineUrl: "/library/mood-roadmap",
  sha256: "6e1521792679c266847e8d9bcdd52f587fef92537b467b34b7ebca5ae0d43fb4",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_DECISION_LOG: LibraryDocument = {
  slug: "mood-decision-log",
  title: "MOOD Decision Log",
  category: "governance",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "All Canon-level decisions, Gate transitions, and HUMAN_DECISION_REQUIRED items. " +
    "Append-only log of MOOD governance state.",
  sourcePath: "docs/mood/DECISION_LOG.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/DECISION_LOG.md",
  onlineUrl: "/library/mood-decision-log",
  sha256: "aeb7f30d1623aa02d449154889a564950158716212175de2a6fa141d5b4acaa2",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const MOOD_INFLIGHT: LibraryDocument = {
  slug: "mood-inflight-changes",
  title: "MOOD In-Flight Change Register",
  category: "governance",
  version: "1.0",
  status: "active",
  language: "bilingual",
  summary:
    "Concurrent branches inventory. 009 DO NOT MERGE WHOLE; Genesis v1.0 SUPERSEDED. " +
    "Track parallel AI / human work.",
  sourcePath: "docs/mood/IN_FLIGHT_CHANGE_REGISTER.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/IN_FLIGHT_CHANGE_REGISTER.md",
  onlineUrl: "/library/mood-inflight-changes",
  sha256: "9681ef7ae394f38a00e5df7389a549ae46c055fbc0fe72e99767a10aa9e99023",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const PUBLIC_BRAND: LibraryDocument = {
  slug: "public-brand-constitution",
  title: "Public Brand Constitution",
  category: "foundation",
  version: "1.0",
  status: "active",
  language: "en",
  summary:
    "Public Brand Constitution for Moodify Music/Player. " +
    "Highest topic-specific Public Brand authority. 014 does NOT modify this canon.",
  sourcePath: "docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md",
  onlineUrl: "/library/public-brand-constitution",
  sha256: "2a35578be75f0f31f0d68e62741d6bad99b5f2db69c44c3e0e8a1bafecfbc7bf",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const PUBLIC_FORM_CANON: LibraryDocument = {
  slug: "public-form-canon",
  title: "Moodify Public Form Canon",
  category: "foundation",
  version: "1.1",
  status: "active",
  language: "en",
  summary:
    "Moodify Music/Player Public Form canon (v1.1). " +
    "Single outward-facing product surface. PLAY-first user app.",
  sourcePath: "docs/canon/CURRENT_CANON.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/canon/CURRENT_CANON.md",
  onlineUrl: "/library/public-form-canon",
  sha256: "77f7763e32692ad1af1c10679e6114f366461961b4b90f0e3c02aaef6092110d",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

// ============================================================
// PROTOCOL (draft — sourcePath present in repo, awaiting 012 review)
// ============================================================

const PROTOCOL_CONTRACTS: LibraryDocument = {
  slug: "canonical-minimum-contracts",
  title: "Canonical Minimum Contracts v1",
  category: "protocol",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "Minimum contract set for Moodify Music/Player canonical surface. " +
    "Awaiting 012 review before being marked active.",
  sourcePath: "docs/contracts/CANONICAL_MINIMUM_CONTRACTS_V1.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/contracts/CANONICAL_MINIMUM_CONTRACTS_V1.md",
  onlineUrl: "/library/canonical-minimum-contracts",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const DATA_PROTOCOL: LibraryDocument = {
  slug: "data-protocol-v1",
  title: "Data Protocol v1",
  category: "protocol",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "Data protocol for the Music contract surface. " +
    "Draft pending 012 review.",
  sourcePath: "docs/contracts/DATA_PROTOCOL_V1.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/contracts/DATA_PROTOCOL_V1.md",
  onlineUrl: "/library/data-protocol-v1",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const PRODUCT_BOUNDARY: LibraryDocument = {
  slug: "product-boundary-contract",
  title: "Product Boundary Contract",
  category: "protocol",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "Boundary contract between MOOD-world and Moodify-product surfaces. " +
    "Draft pending 012 review.",
  sourcePath: "docs/contracts/product-boundary.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/contracts/product-boundary.md",
  onlineUrl: "/library/product-boundary-contract",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const QUARTERLY_FREEZE: LibraryDocument = {
  slug: "quarterly-freeze-1-0",
  title: "Quarterly Freeze 1.0 001",
  category: "protocol",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "First quarterly freeze snapshot. " +
    "Draft pending 012 review.",
  sourcePath: "docs/contracts/QUARTERLY_FREEZE_1_0_001.md",
  sourceSha: REGISTRATION_COMMIT,
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/contracts/QUARTERLY_FREEZE_1_0_001.md",
  onlineUrl: "/library/quarterly-freeze-1-0",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

// ============================================================
// GOVERNANCE
// ============================================================

const MIP_000: LibraryDocument = {
  slug: "mip-000",
  title: "MIP-000 — MOOD Improvement Proposal Process",
  category: "governance",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "Process spec only. Defines lifecycle (Draft → Discussion → Review → Accepted/Rejected → " +
    "Implemented/Archived). No on-chain voting. Awaiting 020 implementation.",
  sourcePath: "docs/mood/governance/MIP-000.md",
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/governance/MIP-000.md",
  onlineUrl: "/library/mip-000",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
  skeleton: {
    chapters: [
      {
        id: "purpose",
        title: "1. Purpose",
        body:
          "MIP-000 defines how MOOD residents propose, discuss, review, and accept or " +
          "reject changes that affect Canon, Protocol, or PORTAL UX. It is process-only; " +
          "no on-chain voting and no token-weighted authority.",
        status: "draft",
      },
      {
        id: "scope",
        title: "2. Scope",
        body:
          "MIPs cover Canon amendments, PROTOCOL module introductions / changes, " +
          "PORTAL IA changes, and Treasury policy changes. Implementation-only changes " +
          "(bug fixes, refactors) do NOT require a MIP.",
        status: "draft",
      },
      {
        id: "lifecycle",
        title: "3. Lifecycle",
        body:
          "Draft → Discussion → Review → Accepted / Rejected → Implemented / Archived. " +
          "Each transition is recorded in docs/mood/DECISION_LOG.md.",
        status: "draft",
      },
      {
        id: "authority",
        title: "4. Authority",
        body:
          "PASS authority is held by humans. Reviewer must be explicitly named in " +
          "DECISION_LOG. Codex may draft MIP text but cannot mark any MIP as Accepted.",
        status: "draft",
      },
      {
        id: "non-goals",
        title: "5. Non-Goals",
        body:
          "MIP-000 does NOT introduce on-chain voting. It does NOT bind Token holdings " +
          "to proposal authority. It does NOT bind proposal outcome to MOOD Token supply.",
        status: "draft",
      },
    ],
  },
};

// ============================================================
// ECONOMICS (DRAFT — parameters UNFROZEN)
// ============================================================

const TOKENOMICS: LibraryDocument = {
  slug: "mood-tokenomics",
  title: "MOOD Tokenomics",
  category: "economics",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Tokenomics parameters are not frozen. Do not interpret as active configuration. " +
    "Pending G10 PASS (Genesis Readiness Review, 024).",
  sourcePath: "docs/mood/economics/TOKENOMICS.md",
  onlineUrl: "/library/mood-tokenomics",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
  skeleton: {
    chapters: [
      {
        id: "status",
        title: "Status",
        body:
          "DRAFT. Parameters are not frozen and do not represent an active token configuration. " +
          "Final Tokenomics will be authored by 024 and ratified by humans before G10 PASS.",
        status: "draft",
      },
      {
        id: "placeholder",
        title: "Placeholder",
        body:
          "This entry exists so 014 Library can register the slot. No supply, emission, or " +
          "distribution curve is committed at this time.",
        status: "placeholder",
      },
    ],
  },
};

const TREASURY_POLICY: LibraryDocument = {
  slug: "mood-treasury-policy",
  title: "MOOD Treasury Policy",
  category: "economics",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Treasury Policy parameters UNFROZEN. Pending G7 (Treasury & Transparency, 021).",
  sourcePath: "docs/mood/economics/TREASURY_POLICY.md",
  onlineUrl: "/library/mood-treasury-policy",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const HOLDER_REWARDS: LibraryDocument = {
  slug: "mood-holder-rewards-policy",
  title: "MOOD Holder Rewards Policy",
  category: "economics",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Holder Rewards Policy UNFROZEN. Pending G7 (021).",
  sourcePath: "docs/mood/economics/HOLDER_REWARDS_POLICY.md",
  onlineUrl: "/library/mood-holder-rewards-policy",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const LEGACY_TOKEN: LibraryDocument = {
  slug: "mood-legacy-token-policy",
  title: "MOOD Legacy Token Policy",
  category: "economics",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Legacy Token Policy. Genesis v1.0 (codex/moodify-classic-reconstruction-001) is FREEZE. " +
    "Old contracts / CA / Distributor are NOT MOOD Token Canon.",
  sourcePath: "docs/mood/economics/LEGACY_TOKEN_POLICY.md",
  onlineUrl: "/library/mood-legacy-token-policy",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const LAUNCH_POLICY: LibraryDocument = {
  slug: "mood-launch-policy",
  title: "MOOD Launch Policy",
  category: "economics",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Launch Policy UNFROZEN. Pending G10 / G11 (024 / 025).",
  sourcePath: "docs/mood/economics/LAUNCH_POLICY.md",
  onlineUrl: "/library/mood-launch-policy",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

// ============================================================
// SECURITY (DRAFT — placeholder, no real audit, no real threat model yet)
// ============================================================

const THREAT_MODEL: LibraryDocument = {
  slug: "mood-threat-model",
  title: "MOOD Threat Model",
  category: "security",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Threat Model slot. Awaiting 022 (Security & Trust Layer). " +
    "No real threat model committed at this time.",
  sourcePath: "docs/mood/security/THREAT_MODEL.md",
  onlineUrl: "/library/mood-threat-model",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const SECURITY_REVIEW: LibraryDocument = {
  slug: "mood-security-review",
  title: "MOOD Security Review",
  category: "security",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Security Review slot. Awaiting 022. " +
    "Historical Genesis v1.0 security docs are NOT audits of any future MOOD Token contract.",
  sourcePath: "docs/mood/security/SECURITY_REVIEW.md",
  onlineUrl: "/library/mood-security-review",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const PRIVACY_REVIEW: LibraryDocument = {
  slug: "mood-privacy-review",
  title: "MOOD Privacy Review",
  category: "security",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Privacy Review slot. Awaiting 022. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/security/PRIVACY_REVIEW.md",
  onlineUrl: "/library/mood-privacy-review",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const INCIDENT_RESPONSE: LibraryDocument = {
  slug: "mood-incident-response",
  title: "MOOD Incident Response",
  category: "security",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Incident Response slot. Awaiting 022. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/security/INCIDENT_RESPONSE.md",
  onlineUrl: "/library/mood-incident-response",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const AUDIT_REPORTS: LibraryDocument = {
  slug: "mood-audit-reports",
  title: "MOOD Audit Reports",
  category: "security",
  version: "0.0",
  status: "archived",
  language: "en",
  summary:
    "Audit Reports slot. Awaiting real audit (024 / 025). " +
    "Historical / Superseded / Legacy Scope — Not an audit of any future MOOD Token contract.",
  sourcePath: "docs/mood/security/AUDIT_REPORTS.md",
  onlineUrl: "/library/mood-audit-reports",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

// ============================================================
// RESEARCH (DRAFT)
// ============================================================

const MACHINE_LISTENING: LibraryDocument = {
  slug: "mood-machine-listening",
  title: "Machine Listening (MOOD)",
  category: "research",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Machine Listening research slot. Awaiting 016 / 017. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/research/MACHINE_LISTENING.md",
  onlineUrl: "/library/mood-machine-listening",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const AUDIO_INTELLIGENCE: LibraryDocument = {
  slug: "mood-audio-intelligence",
  title: "Audio Intelligence (MOOD)",
  category: "research",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Audio Intelligence research slot. Awaiting 016 / 017. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/research/AUDIO_INTELLIGENCE.md",
  onlineUrl: "/library/mood-audio-intelligence",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const PROOF_OF_CONTRIBUTION: LibraryDocument = {
  slug: "mood-proof-of-contribution",
  title: "Proof of Contribution (MOOD)",
  category: "research",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Proof of Contribution research slot. Awaiting 016. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/research/PROOF_OF_CONTRIBUTION.md",
  onlineUrl: "/library/mood-proof-of-contribution",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

const HUMAN_AI_COLLAB: LibraryDocument = {
  slug: "mood-human-ai-collab",
  title: "Human + AI Collaboration (MOOD)",
  category: "research",
  version: "0.0",
  status: "draft",
  language: "en",
  summary:
    "Human + AI Collaboration research slot. Awaiting 016 / 018. " +
    "No content committed at this time.",
  sourcePath: "docs/mood/research/HUMAN_AI_COLLAB.md",
  onlineUrl: "/library/mood-human-ai-collab",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
};

// ============================================================
// CONSTITUTION SKELETON (Draft, no commitment)
// ============================================================

const CONSTITUTION: LibraryDocument = {
  slug: "mood-constitution",
  title: "MOOD Constitution",
  category: "foundation",
  version: "0.1",
  status: "draft",
  language: "en",
  summary:
    "Constitution Skeleton (DRAFT). Honest outline only. " +
    "No section represents a frozen commitment until human ratification.",
  sourcePath: "docs/mood/governance/CONSTITUTION.md",
  githubUrl:
    "https://github.com/huliye24/moodify-ai/blob/main/docs/mood/governance/CONSTITUTION.md",
  onlineUrl: "/library/mood-constitution",
  publishedAt: "2026-08-30",
  updatedAt: "2026-08-30",
  skeleton: {
    chapters: [
      {
        id: "preamble",
        title: "Preamble",
        body:
          "DRAFT outline only. Each chapter below is a candidate topic; " +
          "no section has been ratified by humans. Final wording requires MIP-000 process.",
        status: "draft",
      },
      {
        id: "purpose",
        title: "1. Purpose",
        body: "Outline: define the existence, scope, and purpose of MOOD as an open world.",
        status: "placeholder",
      },
      {
        id: "open-participation",
        title: "2. Open Participation",
        body: "Outline: residency is open; anyone may join WORLD.",
        status: "placeholder",
      },
      {
        id: "identity",
        title: "3. Identity",
        body: "Outline: resident identity boundaries; off-chain default; no SBT.",
        status: "placeholder",
      },
      {
        id: "contribution",
        title: "4. Contribution",
        body: "Outline: contribution recording without automatic token reward.",
        status: "placeholder",
      },
      {
        id: "reputation",
        title: "5. Reputation",
        body: "Outline: reputation snapshots off-chain by default.",
        status: "placeholder",
      },
      {
        id: "ai-agents",
        title: "6. AI Agents",
        body: "Outline: agents as first-class residents with declared capability.",
        status: "placeholder",
      },
      {
        id: "nodes",
        title: "7. Nodes",
        body: "Outline: nodes operate compute / data / storage / verification.",
        status: "placeholder",
      },
      {
        id: "governance",
        title: "8. Governance",
        body: "Outline: MIP process (see MIP-000).",
        status: "placeholder",
      },
      {
        id: "treasury",
        title: "9. Treasury",
        body: "Outline: treasury transparency via 021.",
        status: "placeholder",
      },
      {
        id: "token-activation",
        title: "10. Token Activation",
        body: "Outline: Token activation BLOCKED until G0..G11 ALL PASS.",
        status: "placeholder",
      },
      {
        id: "security",
        title: "11. Security",
        body: "Outline: threat model + audit via 022 / 024.",
        status: "placeholder",
      },
      {
        id: "amendment",
        title: "12. Amendment Process",
        body: "Outline: Canon amendments follow MIP-000 + human sign-off.",
        status: "placeholder",
      },
    ],
  },
};

// ============================================================
// REGISTRY
// ============================================================

export const LIBRARY_DOCUMENTS: LibraryDocument[] = [
  // Foundation (active)
  MOOD_CANON,
  MOOD_ARCHITECTURE,
  MOOD_PRODUCT_RELATIONSHIP,
  PUBLIC_BRAND,
  PUBLIC_FORM_CANON,
  CONSTITUTION,

  // Governance (active 011 docs + draft MIP-000)
  MOOD_LAUNCH_GATE,
  MOOD_ASSET_CLASSIFICATION,
  MOOD_ROADMAP,
  MOOD_DECISION_LOG,
  MOOD_INFLIGHT,
  MIP_000,

  // Protocol (draft contracts)
  PROTOCOL_CONTRACTS,
  DATA_PROTOCOL,
  PRODUCT_BOUNDARY,
  QUARTERLY_FREEZE,

  // Economics (all draft, parameters unfrozen)
  TOKENOMICS,
  TREASURY_POLICY,
  HOLDER_REWARDS,
  LEGACY_TOKEN,
  LAUNCH_POLICY,

  // Security (all draft / archived, no real audit)
  THREAT_MODEL,
  SECURITY_REVIEW,
  PRIVACY_REVIEW,
  INCIDENT_RESPONSE,
  AUDIT_REPORTS,

  // Research (all draft)
  MACHINE_LISTENING,
  AUDIO_INTELLIGENCE,
  PROOF_OF_CONTRIBUTION,
  HUMAN_AI_COLLAB,
];

const CATEGORY_LABEL: Record<LibraryDocument["category"], string> = {
  foundation: "Foundation",
  protocol: "Protocol",
  governance: "Governance",
  economics: "Economics",
  security: "Security",
  research: "Research",
};

export const CATEGORY_ORDER: Array<LibraryDocument["category"]> = [
  "foundation",
  "protocol",
  "governance",
  "economics",
  "security",
  "research",
];

export function getDocumentBySlug(slug: string): LibraryDocument | null {
  return LIBRARY_DOCUMENTS.find((d) => d.slug === slug) ?? null;
}

export function listDocuments(filter?: LibraryFilter): LibraryDocument[] {
  let docs = [...LIBRARY_DOCUMENTS];
  if (filter?.category) docs = docs.filter((d) => d.category === filter.category);
  if (filter?.status) docs = docs.filter((d) => d.status === filter.status);
  if (filter?.language) docs = docs.filter((d) => d.language === filter.language);
  if (filter?.query) {
    const q = filter.query.toLowerCase();
    docs = docs.filter(
      (d) =>
        d.title.toLowerCase().includes(q) ||
        d.summary.toLowerCase().includes(q) ||
        d.slug.includes(q),
    );
  }
  return docs;
}

export function listByCategory(): LibraryCategoryGroup[] {
  return CATEGORY_ORDER.map((category) => ({
    category,
    label: CATEGORY_LABEL[category],
    documents: listDocuments({ category }),
  })).filter((group) => group.documents.length > 0);
}

export function listFeatured(): LibraryDocument[] {
  // Active docs in foundation / governance are surfaced first.
  return LIBRARY_DOCUMENTS.filter(
    (d) =>
      d.status === "active" &&
      (d.category === "foundation" || d.category === "governance"),
  );
}

export function listDraft(): LibraryDocument[] {
  return LIBRARY_DOCUMENTS.filter((d) => d.status === "draft");
}

export function listArchived(): LibraryDocument[] {
  return LIBRARY_DOCUMENTS.filter(
    (d) => d.status === "superseded" || d.status === "archived",
  );
}

export function getOnlineUrl(doc: LibraryDocument): string {
  return doc.onlineUrl ?? `/library/${doc.slug}`;
}
