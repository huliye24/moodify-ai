/**
 * MOOD-TREASURY-021: Treasury Page
 *
 * Public transparency page for protocol financial data.
 * Read-only. Renders HONEST inactive state when no treasury exists.
 *
 * SAFETY:
 *   - No transfer / execution UI
 *   - No private keys, mnemonics, seeds
 *   - No fake balances
 *   - No fabricated USD valuations
 */

import { Metadata } from "next";
import Link from "next/link";
import {
  buildTreasurySnapshot,
  type TreasuryActivationState,
  type TreasurySnapshot,
} from "@/lib/treasury/model";

export const metadata: Metadata = {
  title: "Treasury | Moodify Protocol",
  description:
    "Public treasury transparency layer for MOOD protocol. Currently inactive.",
  robots: { index: true, follow: true },
};

function StatusBadge({ status }: { status: TreasuryActivationState }) {
  const colors: Record<TreasuryActivationState, string> = {
    inactive: "bg-gray-100 text-gray-700",
    observed: "bg-amber-100 text-amber-800",
    "policy-ready": "bg-blue-100 text-blue-800",
    active: "bg-green-100 text-green-800",
    paused: "bg-red-100 text-red-800",
  };
  const labels: Record<TreasuryActivationState, string> = {
    inactive: "Not Activated",
    observed: "Observed (Candidate)",
    "policy-ready": "Policy-Ready",
    active: "Active",
    paused: "Paused",
  };
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${colors[status]}`}
    >
      {labels[status]}
    </span>
  );
}

function HeroStatus({ status }: { status: TreasuryActivationState }) {
  if (status === "inactive") {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-3">
          Treasury Status: Not Activated
        </h2>
        <p className="text-gray-700 mb-4">
          MOOD is building its treasury policy and transparency layer before
          activating protocol-controlled funds.
        </p>
        <p className="text-gray-600 text-sm">
          No real treasury balance exists. This page will display verified
          balances once an account is activated through governance and human
          approval.
        </p>
      </div>
    );
  }
  if (status === "observed") {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-amber-900 mb-3">
          Treasury Status: Observed (Candidate)
        </h2>
        <p className="text-amber-800">
          Candidate addresses have been identified but are NOT yet authorized
          as protocol Treasury. Activation requires an accepted MIP and explicit
          human approval.
        </p>
      </div>
    );
  }
  if (status === "policy-ready") {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-blue-900 mb-3">
          Treasury Status: Policy-Ready
        </h2>
        <p className="text-blue-800">
          Policy and controls are in place. Activation pending governance
          decision (MIP) and human approval.
        </p>
      </div>
    );
  }
  if (status === "active") {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-green-900 mb-3">
          Treasury Status: Active
        </h2>
        <p className="text-green-800">
          Activated by governance. Last sync timestamp shown below.
        </p>
      </div>
    );
  }
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-8">
      <h2 className="text-2xl font-bold text-red-900 mb-3">
        Treasury Status: Paused
      </h2>
      <p className="text-red-800">
        Treasury is temporarily paused. See governance records for reason.
      </p>
    </div>
  );
}

export default function TreasuryPage() {
  // v1: HONEST inactive state.
  const snapshot: TreasurySnapshot = buildTreasurySnapshot();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">MOOD Treasury</h1>
            <p className="text-gray-600 mt-2">
              Public treasury transparency layer
            </p>
          </div>
          <StatusBadge status={snapshot.treasuryStatus} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Hero */}
        <HeroStatus status={snapshot.treasuryStatus} />

        {/* Policy */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Policy</h2>
          <p className="text-gray-700 mb-3">
            Treasury policy defines allowed uses, approval authority, signer
            model, and what 021 explicitly does NOT do (auto-transfer, AI
            execution, etc.).
          </p>
          <Link
            href="/transparency"
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            See also: Protocol Transparency →
          </Link>
        </section>

        {/* Accounts */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Accounts</h2>
          {snapshot.accounts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No treasury accounts publicly disclosed yet.</p>
              <p className="text-sm mt-2">
                Treasury configuration pending human approval and MIP acceptance.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Name
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Type
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Status
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Address
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {snapshot.accounts.map((account) => (
                    <tr key={account.id}>
                      <td className="px-4 py-3 font-medium">{account.name}</td>
                      <td className="px-4 py-3 text-gray-600">{account.type}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={account.status} />
                      </td>
                      <td className="px-4 py-3 font-mono text-sm text-gray-500">
                        {account.address ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Verified Assets */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Verified Assets
          </h2>
          {snapshot.assets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No verified assets.</p>
              <p className="text-sm mt-2">
                Assets will appear here once a treasury account is active and
                balances are verified on-chain.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {snapshot.assets.map((asset, i) => (
                <div
                  key={i}
                  className="border border-gray-100 rounded-lg p-4 flex justify-between items-center"
                >
                  <div>
                    <p className="font-medium">{asset.assetId}</p>
                    <p className="text-xs text-gray-500">
                      {asset.assetType} · {asset.verificationState}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{asset.quantity ?? "—"}</p>
                    {asset.valuationUsd ? (
                      <p className="text-sm text-gray-600">
                        ${asset.valuationUsd}
                      </p>
                    ) : (
                      <p className="text-sm text-gray-400">
                        Valuation not available
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Revenue Sources */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Revenue Sources
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Source
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Status
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Realized (this period)
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Notes
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {snapshot.revenue.map((r) => (
                  <tr key={r.source}>
                    <td className="px-4 py-3 font-medium">{r.source}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          r.status === "ACTIVE"
                            ? "bg-green-100 text-green-800"
                            : r.status === "PLANNED"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {r.realizedThisPeriod ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {r.notes ?? ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Allocations */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Allocations
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Category
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Status
                  </th>
                  <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                    Reason
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {snapshot.allocations.map((a) => (
                  <tr key={a.category}>
                    <td className="px-4 py-3 font-medium">{a.category}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          a.status === "ENABLED"
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-200 text-gray-700"
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {a.reason ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Executions */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Executions
          </h2>
          {snapshot.executions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No executions recorded.</p>
              <p className="text-sm mt-2">
                Executions will appear here once the treasury is active.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {snapshot.executions.map((e) => (
                <div
                  key={e.id}
                  className="border border-gray-100 rounded-lg p-4"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">
                        {e.action} · {e.amount ?? "—"} {e.assetId ?? ""}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">{e.reason}</p>
                      {e.governanceRef && (
                        <p className="text-xs text-blue-600 mt-1">
                          Governance: {e.governanceRef}
                        </p>
                      )}
                    </div>
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                      {e.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Governance References */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Governance References
          </h2>
          <ul className="space-y-2">
            {snapshot.governanceRefs.map((ref) => (
              <li key={ref} className="text-sm text-gray-700">
                <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                  {ref}
                </code>
              </li>
            ))}
          </ul>
        </section>

        {/* Reports */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Reports</h2>
          <p className="text-gray-700 text-sm">
            Treasury reports are stored under{" "}
            <code className="bg-gray-100 px-2 py-1 rounded text-xs">
              docs/mood/treasury/reports/
            </code>
            . No reports have been generated for v1 because there are no
            treasury operations to report on. Future reports will follow the
            schema in{" "}
            <code className="bg-gray-100 px-2 py-1 rounded text-xs">
              021_REPORT_SCHEMA.md
            </code>
            .
          </p>
        </section>

        {/* Risks */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">Risks</h2>
          <ul className="space-y-2">
            {snapshot.risks.map((risk, i) => (
              <li key={i} className="text-sm text-gray-700 flex items-start">
                <span className="text-amber-500 mr-2">⚠</span>
                {risk}
              </li>
            ))}
          </ul>
        </section>

        {/* Methodology */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-3">
            Methodology & Limitations
          </h2>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-2">
            <li>RPC reads may fail or be stale.</li>
            <li>No valuation oracle is currently approved.</li>
            <li>
              USD valuations are only displayed when a reliable source exists.
            </li>
            <li>
              Future token economics (trading tax, holder rewards, liquidity
              yield) remain launch-gated until 024/025.
            </li>
            <li>
              Reconciliation mismatches are shown, not auto-corrected.
            </li>
            <li>
              Single-operator custody is a known v1 risk. Multi-sig requires an
              accepted MIP.
            </li>
            <li>AI agents have observer / analyst role only; no transfer authority.</li>
          </ul>
        </section>

        {/* API */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Programmatic Access
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Treasury snapshot is available as JSON:
          </p>
          <code className="bg-white px-3 py-2 rounded text-sm font-mono block">
            GET /api/protocol/treasury
          </code>
          <code className="bg-white px-3 py-2 rounded text-sm font-mono block mt-2">
            GET /api/protocol/treasury/status
          </code>
        </section>
      </main>

      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-gray-500">
        <p>MOOD-TREASURY-021: Treasury &amp; Transparency</p>
        <p className="mt-1">
          This page is read-only. No token transfers are performed.
        </p>
        <p className="mt-1">
          Generated at{" "}
          <code className="bg-gray-100 px-1 py-0.5 rounded text-xs">
            {snapshot.generatedAt}
          </code>
        </p>
      </footer>
    </div>
  );
}
