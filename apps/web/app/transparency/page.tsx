/**
 * MOOD-GENESIS-007: Transparency Page
 *
 * Public transparency layer for protocol assets.
 * Read-only. No sensitive data exposed.
 */

import { Metadata } from "next";
import Link from "next/link";
import { MOOD_TOKEN } from "@/lib/mood-token";
import {
  getPublicTreasuryAccounts,
  TREASURY_CONFIG,
  getMoodTokenConfig,
} from "@/lib/mood-treasury";
import { getTotalSupply, formatMood } from "@/lib/mood-chain";
import { getDb } from "@/db";
import { genesisParticipants } from "@/db/schema";
import { sql } from "drizzle-orm";

export const metadata: Metadata = {
  title: "Transparency | Moodify Protocol",
  description: "Public transparency layer for MOOD token and protocol assets",
};

/** Format number with commas */
function formatNumber(num: number | string): string {
  const n = typeof num === "string" ? parseFloat(num) : num;
  return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

/** Format percentage */
function formatPercentage(num: number): string {
  return `${num.toFixed(2)}%`;
}

/** Shorten address */
function shortenAddress(addr: string): string {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

export default async function TransparencyPage() {
  // Fetch data
  const tokenConfig = getMoodTokenConfig();
  const totalSupply = await getTotalSupply();
  const publicAccounts = getPublicTreasuryAccounts();

  // Get Genesis stats
  const db = getDb();
  const genesisStats = await db
    .select({
      total: sql<number>`COUNT(*)`,
      allocated: sql<number>`SUM(CASE WHEN ${genesisParticipants.status} = 'allocated' THEN 1 ELSE 0 END)`,
    })
    .from(genesisParticipants)
    .get();

  const totalSupplyMood = formatMood(totalSupply.value);
  const isStale = totalSupply.isStale;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Protocol Transparency</h1>
          <p className="text-gray-600 mt-2">
            Public transparency layer for MOOD token and protocol assets
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* A. Protocol Asset Overview */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Protocol Asset Overview
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Token</p>
              <p className="text-lg font-medium">{tokenConfig.name}</p>
              <p className="text-sm text-gray-600">{tokenConfig.symbol}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Network</p>
              <p className="text-lg font-medium">{tokenConfig.network}</p>
              <p className="text-sm text-gray-600">Chain ID: {tokenConfig.chainId}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Decimals</p>
              <p className="text-lg font-medium">{tokenConfig.decimals}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Total Supply</p>
              <p className="text-lg font-medium">{formatNumber(totalSupplyMood)} MOOD</p>
              {isStale && (
                <p className="text-xs text-amber-600 mt-1">From config (RPC unavailable)</p>
              )}
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-4">
            <a
              href={tokenConfig.explorerUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              View on BscScan →
            </a>
            <a
              href={tokenConfig.tradeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              Trade on PancakeSwap →
            </a>
          </div>

          <div className="mt-4 bg-gray-100 rounded-lg p-3">
            <p className="text-sm text-gray-600">
              <span className="font-medium">Contract:</span>{" "}
              <code className="text-xs bg-white px-2 py-1 rounded">{tokenConfig.address}</code>
            </p>
          </div>
        </section>

        {/* B. Supply Accounting */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Supply Accounting</h2>

          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <span className="text-gray-600">Total Supply</span>
              <span className="font-medium">{formatNumber(totalSupplyMood)} MOOD</span>
            </div>

            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <span className="text-gray-600">Protocol-Controlled Balance</span>
              <span className="font-medium text-gray-400">Not yet published</span>
            </div>

            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <span className="text-gray-600">Treasury/Reserve Balance</span>
              <span className="font-medium text-gray-400">Not yet published</span>
            </div>

            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <span className="text-gray-600">Genesis Allocated</span>
              <span className="font-medium text-gray-400">Not yet published</span>
            </div>

            <div className="flex justify-between items-center py-3 border-b border-gray-100">
              <span className="text-gray-600">Genesis Claimed/Distributed</span>
              <span className="font-medium text-gray-400">Not yet published</span>
            </div>

            <div className="flex justify-between items-center py-3">
              <span className="text-gray-600">Contribution Rewards Pending</span>
              <span className="font-medium text-gray-400">Not yet published</span>
            </div>
          </div>

          <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
            <p className="text-sm text-amber-800">
              <strong>Note:</strong> Wallet balance ≠ circulating supply. Circulating
              supply methodology not yet formally published.
            </p>
          </div>
        </section>

        {/* C. Treasury Accounts */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Treasury Accounts</h2>

          {publicAccounts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No treasury accounts publicly disclosed yet.</p>
              <p className="text-sm mt-2">
                Treasury configuration pending human approval.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Label
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Category
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Address
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      Balance
                    </th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-gray-700">
                      % of Supply
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {publicAccounts.map((account) => (
                    <tr key={account.id}>
                      <td className="px-4 py-3">
                        <span className="font-medium">{account.label}</span>
                        {account.notes && (
                          <p className="text-xs text-gray-500">{account.notes}</p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                        >
                          {account.category}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <a
                          href={`${tokenConfig.explorerUrl}/address/${account.address}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 font-mono text-sm"
                        >
                          {shortenAddress(account.address)}
                        </a>
                      </td>
                      <td className="px-4 py-3 text-gray-400">Pending read</td>
                      <td className="px-4 py-3 text-gray-400">--</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* D. Genesis */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Genesis</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Registered Participants</p>
              <p className="text-2xl font-semibold">{genesisStats?.total || 0}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Allocated Participants</p>
              <p className="text-2xl font-semibold">{genesisStats?.allocated || 0}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Genesis Allocation</p>
              <p className="text-2xl font-semibold text-gray-400">Pending</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Claimed MOOD</p>
              <p className="text-lg font-medium text-gray-400">Not yet published</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Unclaimed MOOD</p>
              <p className="text-lg font-medium text-gray-400">Not yet published</p>
            </div>
          </div>
        </section>

        {/* E. Contribution Network */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Contribution Network</h2>

          <div className="text-center py-8 text-gray-500">
            <p>Contribution network aggregates not yet implemented.</p>
            <p className="text-sm mt-2">See Package 006 for contribution reward system.</p>
          </div>
        </section>

        {/* F. Liquidity */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Liquidity</h2>

          <div className="text-center py-8 text-gray-500">
            <p>Liquidity positions not yet verified.</p>
            <p className="text-sm mt-2">PancakeSwap pool data pending verification.</p>
          </div>
        </section>

        {/* G. Methodology */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Methodology</h2>

          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Circulating Supply</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">
                  Status: <span className="font-medium">{TREASURY_CONFIG.circulatingSupply.status}</span>
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  {TREASURY_CONFIG.circulatingSupply.description}
                </p>
              </div>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Data Sources</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>BNB Smart Chain RPC (bsc-dataseed.binance.org)</li>
                <li>Moodify Genesis database</li>
                <li>Approved Package 004 snapshot artifacts</li>
                <li>On-chain event logs (when indexed)</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Limitations</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>RPC reads may fail or be stale</li>
                <li>Database aggregates reflect last-known state</li>
                <li>On-chain events require indexing</li>
                <li>Circulating supply methodology not yet approved</li>
              </ul>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">Last Updated</h3>
              <p className="text-sm text-gray-600">
                {new Date().toISOString()}
              </p>
            </div>
          </div>
        </section>

        {/* API Link */}
        <section className="bg-gray-100 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">API</h2>
          <p className="text-sm text-gray-600 mb-4">
            Access transparency data programmatically:
          </p>
          <code className="bg-white px-3 py-2 rounded text-sm font-mono">
            GET /api/protocol/transparency
          </code>
        </section>
      </main>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-gray-500">
        <p>MOOD-GENESIS-007: Transparency & Treasury</p>
        <p className="mt-1">
          This page is read-only. No token transfers are performed.
        </p>
      </footer>
    </div>
  );
}
