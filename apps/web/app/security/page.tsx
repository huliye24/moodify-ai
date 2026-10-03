/**
 * MOOD-SECURITY-022: Security Page
 *
 * Public security transparency page. Renders HONEST security status.
 * Read-only. No secrets, no internal hostnames.
 */

import { Metadata } from "next";
import { buildSecurityStatusPayload } from "@/lib/security/model";

export const metadata: Metadata = {
  title: "Security | Moodify Protocol",
  description:
    "Public security transparency for MOOD protocol. Honest disclosure of controls, findings, and trust claims.",
  robots: { index: true, follow: true },
};

function GateStatusBadge({
  status,
}: {
  status: "passed" | "open" | "blocked" | "not-applicable";
}) {
  const colors = {
    passed: "bg-green-100 text-green-800",
    open: "bg-amber-100 text-amber-800",
    blocked: "bg-red-100 text-red-800",
    "not-applicable": "bg-gray-100 text-gray-700",
  };
  const labels = {
    passed: "Passed",
    open: "Open",
    blocked: "Blocked",
    "not-applicable": "N/A",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[status]}`}
    >
      {labels[status]}
    </span>
  );
}

function SeverityBadge({
  severity,
}: {
  severity: "P0" | "P1" | "P2" | "P3" | "Info";
}) {
  const colors = {
    P0: "bg-red-100 text-red-800",
    P1: "bg-orange-100 text-orange-800",
    P2: "bg-amber-100 text-amber-800",
    P3: "bg-blue-100 text-blue-800",
    Info: "bg-gray-100 text-gray-700",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[severity]}`}
    >
      {severity}
    </span>
  );
}

function FindingStatusBadge({
  status,
}: {
  status: "open" | "mitigated" | "deferred" | "closed";
}) {
  const colors = {
    open: "bg-red-100 text-red-800",
    mitigated: "bg-blue-100 text-blue-800",
    deferred: "bg-gray-100 text-gray-700",
    closed: "bg-green-100 text-green-800",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[status]}`}
    >
      {status}
    </span>
  );
}

function ClaimStatusBadge({
  status,
}: {
  status: "verified" | "partial" | "open";
}) {
  const colors = {
    verified: "bg-green-100 text-green-800",
    partial: "bg-amber-100 text-amber-800",
    open: "bg-gray-100 text-gray-700",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[status]}`}
    >
      {status}
    </span>
  );
}

export default function SecurityPage() {
  const payload = buildSecurityStatusPayload();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            MOOD Security &amp; Trust
          </h1>
          <p className="text-gray-600 mt-2">
            Public security transparency layer. Honest disclosure of controls,
            findings, and trust claims.
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Hero / Status */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Current Security Status
              </h2>
              <p className="text-gray-700 mt-2 text-sm">
                Independent third-party security audit:{" "}
                <span className="font-medium">Not completed</span>.
              </p>
            </div>
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                payload.overallStatus === "ok"
                  ? "bg-green-100 text-green-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {payload.overallStatus === "ok"
                ? "Operational"
                : "Open Findings"}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Custodian Model</p>
              <p className="font-medium capitalize">
                {payload.summary.custodianModel}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Treasury</p>
              <p className="font-medium">
                {payload.summary.treasuryActive ? "Active" : "Not Activated"}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Auto-Payout</p>
              <p className="font-medium">
                {payload.summary.autoPayoutEnabled ? "Enabled" : "Disabled"}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">AI Signer Authority</p>
              <p className="font-medium">
                {payload.summary.aiSignerEnabled ? "Enabled" : "Disabled"}
              </p>
            </div>
          </div>
        </section>

        {/* Staging Gate */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Staging Security Gate
          </h2>
          <p className="text-gray-700 text-sm mb-4">
            Required for 023 Public Staging. See{" "}
            <code className="bg-gray-100 px-2 py-1 rounded text-xs">
              docs/mood/security/022_STAGING_SECURITY_GATE.md
            </code>
            .
          </p>
          <div className="space-y-2">
            {payload.stagingGate.gates.map((gate) => (
              <div
                key={gate.id}
                className="flex items-center justify-between border border-gray-100 rounded-lg p-3"
              >
                <div>
                  <p className="font-medium text-sm">
                    {gate.id}: {gate.name}
                  </p>
                  {gate.evidence && (
                    <p className="text-xs text-gray-500">{gate.evidence}</p>
                  )}
                </div>
                <GateStatusBadge status={gate.status} />
              </div>
            ))}
          </div>
        </section>

        {/* Trust Claims */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Public Trust Claims
          </h2>
          <p className="text-gray-700 text-sm mb-4">
            Every claim must have evidence. No evidence → no claim.
          </p>
          <div className="space-y-3">
            {payload.trustClaims.map((claim) => (
              <div
                key={claim.id}
                className="border border-gray-100 rounded-lg p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-medium text-sm">
                      {claim.id}: {claim.claim}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Evidence:{" "}
                      <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                        {claim.evidenceRef}
                      </code>
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Last Verified: {claim.lastVerified} · Scope:{" "}
                      {claim.scope}
                    </p>
                  </div>
                  <ClaimStatusBadge status={claim.status} />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Findings */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Findings Register
          </h2>
          <p className="text-gray-700 text-sm mb-4">
            Severity: P0 (critical) → P1 (high) → P2 (medium) → P3 (low) → Info.
          </p>
          <div className="space-y-3">
            {payload.findings.map((finding) => (
              <div
                key={finding.id}
                className="border border-gray-100 rounded-lg p-4"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="font-medium text-sm">
                      {finding.id}: {finding.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Affected: {finding.affected.join(", ")}
                    </p>
                    {finding.evidenceRef && (
                      <p className="text-xs text-gray-500 mt-1">
                        Evidence:{" "}
                        <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                          {finding.evidenceRef}
                        </code>
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={finding.severity} />
                    <FindingStatusBadge status={finding.status} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Channels */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Responsible Disclosure
          </h2>
          <p className="text-gray-700 text-sm mb-2">
            Security contact channel:{" "}
            <span className="font-medium">
              {payload.channels.securityContact}
            </span>
          </p>
          <p className="text-gray-700 text-sm mb-2">
            Disclosure policy:{" "}
            <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
              {payload.channels.disclosurePolicy}
            </code>
          </p>
          <p className="text-gray-700 text-sm">
            Incident response:{" "}
            <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">
              {payload.incidentResponse}
            </code>
          </p>
        </section>

        {/* Audit History */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Audit &amp; Review History
          </h2>
          <p className="text-gray-700 text-sm">
            Independent third-party security audit:{" "}
            <span className="font-medium">Not completed</span>.
          </p>
          <p className="text-gray-700 text-sm mt-2">
            Internal reviews completed: 022 Security &amp; Trust Layer (this
            session). 021 Treasury &amp; Transparency (prior session).
          </p>
        </section>

        {/* Methodology */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Methodology &amp; Limitations
          </h2>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
            <li>
              This page is HONEST. Where audits are not complete, we say so.
            </li>
            <li>
              No claim is made of &quot;100% secure&quot;, &quot;fully
              decentralized&quot;, or &quot;audited by industry leaders&quot;.
            </li>
            <li>
              v1 single-operator custody is openly acknowledged as a risk.
            </li>
            <li>
              Multi-sig migration requires an accepted MIP (category =
              treasury).
            </li>
            <li>
              022 is the BASELINE. Further hardening continues with 023 and
              post-023 work.
            </li>
          </ul>
        </section>

        {/* API */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Programmatic Access
          </h2>
          <code className="bg-white px-3 py-2 rounded text-sm font-mono block">
            GET /api/security/status
          </code>
        </section>
      </main>

      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-gray-500">
        <p>MOOD-SECURITY-022: Security &amp; Trust Layer</p>
        <p className="mt-1">
          Generated at{" "}
          <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">
            {payload.generatedAt}
          </code>
        </p>
      </footer>
    </div>
  );
}
