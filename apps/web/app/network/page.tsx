"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
// import { ExternalLink, RefreshCw, Users, CheckCircle, AlertCircle, Clock } from "lucide-react";
import NetworkHealthMonitor from "@/components/network-health-monitor";
import ActivityFeed from "@/components/network-activity-feed";

// Type definitions for network metrics
type MetricValue = {
  value: number | null;
  state: "available" | "unavailable" | "coming-soon" | "stale";
  source: string;
  updatedAt?: string;
  definition?: string;
};

type NetworkOverview = {
  status: "operational" | "degraded" | "partial" | "maintenance" | "unknown";
  generatedAt: string;
  metrics: {
    residents?: MetricValue;
    totalResidents?: MetricValue;
    newResidents?: MetricValue;
    contributors?: MetricValue;
    approvedContributors?: MetricValue;
    openTasks?: MetricValue;
    totalTasks?: MetricValue;
    draftTasks?: MetricValue;
    pausedTasks?: MetricValue;
    submissions?: MetricValue;
    pendingReview?: MetricValue;
    approvedContributions?: MetricValue;
    rejectedSubmissions?: MetricValue;
    withdrawnSubmissions?: MetricValue;
    reputationEvents?: MetricValue;
    totalReputation?: MetricValue;
    pendingRewards?: MetricValue;
    pendingRewardMood?: MetricValue;
    cancelledRewards?: MetricValue;
    agents?: MetricValue;
    nodes?: MetricValue;
    governance?: MetricValue;
    treasury?: MetricValue;
  };
};

// Status badge colors
const getStatusColor = (status: string) => {
  switch (status) {
    case "operational":
      return "bg-green-500/20 text-green-700 border-green-200";
    case "degraded":
      return "bg-yellow-500/20 text-yellow-700 border-yellow-200";
    case "partial":
      return "bg-orange-500/20 text-orange-700 border-orange-200";
    case "maintenance":
      return "bg-blue-500/20 text-blue-700 border-blue-200";
    case "unknown":
      return "bg-gray-500/20 text-gray-700 border-gray-200";
    default:
      return "bg-gray-500/20 text-gray-700 border-gray-200";
  }
};

// Metric display component
const MetricCard = ({ title, value, definition, source }: {
  title: string;
  value: MetricValue;
  definition?: string;
  source?: string;
}) => {
  if (value.state === "coming-soon") {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
            <p className="text-xl font-bold text-gray-400">Not Available</p>
            <p className="text-xs text-gray-500 mt-1">Coming in Package {source.split("-")[1]}</p>
          </div>
          <Clock className="h-8 w-8 text-gray-400" />
        </div>
      </Card>
    );
  }

  if (value.state === "unavailable") {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
            <p className="text-xl font-bold text-gray-400">Not Available</p>
            <p className="text-xs text-gray-500 mt-1">No data available</p>
          </div>
          <AlertCircle className="h-8 w-8 text-gray-400" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
          <p className="text-3xl font-bold">
            {typeof value.value === 'number' ? value.value.toLocaleString() : "—"}
          </p>
          {definition && (
            <p className="text-xs text-gray-500 mt-2">{definition}</p>
          )}
          <p className="text-xs text-gray-400 mt-1">Source: {source}</p>
        </div>
        {/* <Users className="h-8 w-8 text-gray-400" /> */}
      </div>
    </Card>
  );
};

export default function NetworkPage() {
  const [overview, setOverview] = useState<NetworkOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchOverview = async () => {
    try {
      const response = await fetch("/api/network/overview");
      const data = await response.json();
      setOverview(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch network overview:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    // Refresh every 5 minutes
    const interval = setInterval(fetchOverview, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Skeleton className="h-12 w-64 mb-4" />
          <Skeleton className="h-8 w-96" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[...Array(9)].map((_, i) => (
            <Card key={i} className="p-6">
              <Skeleton className="h-6 w-32 mb-2" />
              <Skeleton className="h-12 w-24" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">Network Observatory</h1>
          <p className="text-gray-600 mb-8">Failed to load network data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold">MOOD Network</h1>
          <div className="flex items-center gap-4">
            {lastUpdated && (
              <span className="text-sm text-gray-500">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            <button
              onClick={fetchOverview}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>
        </div>
        <p className="text-gray-600 mb-4">
          A living view of the world being built.
        </p>
        <div className="flex items-center gap-4">
          <Badge className={getStatusColor(overview.status)}>
            {overview.status.charAt(0).toUpperCase() + overview.status.slice(1)}
          </Badge>
          <span className="text-sm text-gray-500">
            Generated at {new Date(overview.generatedAt).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Residents Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Residents</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Active Residents"
            value={overview.metrics.residents!}
            definition="Real people with verified identity"
            source="users"
          />
          <MetricCard
            title="Total Registered"
            value={overview.metrics.totalResidents!}
            definition="All-time registered count"
            source="users"
          />
          <MetricCard
            title="New Residents (30d)"
            value={overview.metrics.newResidents!}
            definition="Monthly growth trend"
            source="users"
          />
        </div>
      </section>

      {/* Contributors Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Contributors</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            title="Active Contributors"
            value={overview.metrics.contributors!}
            definition="Residents with submitted work"
            source="contributionSubmissions"
          />
          <MetricCard
            title="Approved Contributors"
            value={overview.metrics.approvedContributors!}
            definition="Residents with approved contributions"
            source="contributionSubmissions"
          />
        </div>
      </section>

      {/* Tasks Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Tasks</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Open Tasks"
            value={overview.metrics.openTasks!}
            definition="Currently accepting submissions"
            source="contributionTasks"
          />
          <MetricCard
            title="Total Tasks"
            value={overview.metrics.totalTasks!}
            definition="All-time task count"
            source="contributionTasks"
          />
          <MetricCard
            title="Draft Tasks"
            value={overview.metrics.draftTasks!}
            definition="Not yet published"
            source="contributionTasks"
          />
          <MetricCard
            title="Paused Tasks"
            value={overview.metrics.pausedTasks!}
            definition="Temporarily closed"
            source="contributionTasks"
          />
        </div>
      </section>

      {/* Submissions Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Submissions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Total Submissions"
            value={overview.metrics.submissions!}
            definition="All-time submission count"
            source="contributionSubmissions"
          />
          <MetricCard
            title="Pending Review"
            value={overview.metrics.pendingReview!}
            definition="Awaiting review"
            source="contributionSubmissions"
          />
          <MetricCard
            title="Approved"
            value={overview.metrics.approvedContributions!}
            definition="Successfully completed"
            source="contributionSubmissions"
          />
        </div>
      </section>

      {/* Reputation Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Reputation</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            title="Reputation Events"
            value={overview.metrics.reputationEvents!}
            definition="Total reputation events"
            source="reputationEvents"
          />
          <MetricCard
            title="Total Reputation"
            value={overview.metrics.totalReputation!}
            definition="Points issued to community"
            source="reputationEvents"
          />
        </div>
      </section>

      {/* Rewards Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Rewards</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            title="Pending Rewards"
            value={overview.metrics.pendingRewards!}
            definition="Awards awaiting distribution"
            source="rewardEvents"
          />
          <MetricCard
            title="Pending MOOD Amount"
            value={overview.metrics.pendingRewardMood!}
            definition="Total MOOD tokens pending"
            source="rewardEvents"
          />
        </div>
      </section>

      {/* Treasury Section (MOOD-TREASURY-021) */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Treasury</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard
            title="Treasury Status"
            value={overview.metrics.treasury!}
            definition={
              (overview.metrics.treasury as any)?.subMetrics?.treasuryStatus ??
              "Not Activated"
            }
            source="MOOD-TREASURY-021"
          />
          <MetricCard
            title="Verified Accounts"
            value={
              (overview.metrics.treasury as any)?.subMetrics?.verifiedAccounts ??
              0
            }
            definition="Active treasury accounts (verified on-chain)"
            source="MOOD-TREASURY-021"
          />
          <MetricCard
            title="Future Economics"
            value={
              (overview.metrics.treasury as any)?.subMetrics?.economics ??
              "Launch-Gated"
            }
            definition="Trading tax / holder rewards / LP yield"
            source="MOOD-TREASURY-021"
          />
          <Card className="p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium">View Treasury</h3>
              <Badge variant="secondary">Public</Badge>
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Public treasury transparency layer.
            </p>
            <a
              href="/treasury"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Open /treasury →
            </a>
          </Card>
        </div>
      </section>

      {/* Coming Soon Section */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Coming Soon</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <MetricCard
            title="Agents"
            value={overview.metrics.agents!}
            definition="Registered AI agents"
            source="MOOD-AGENTS-018"
          />
          <MetricCard
            title="Nodes"
            value={overview.metrics.nodes!}
            definition="Network infrastructure"
            source="MOOD-NODES-019"
          />
          <MetricCard
            title="Governance"
            value={overview.metrics.governance!}
            definition="Community proposals"
            source="MOOD-GOVERNANCE-020"
          />
        </div>
      </section>

      {/* Data Sources */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold mb-4">Data Sources</h2>
        <div className="text-sm text-gray-600 space-y-2">
          <p>• Residents: Passport 015 users table</p>
          <p>• Contributors: Contribution Network 016</p>
          <p>• Tasks & Submissions: Contribution Network 016</p>
          <p>• Reputation & Rewards: Contribution Network 016</p>
        </div>
      </section>

      {/* Network Health Monitor */}
      <section className="mb-12">
        <NetworkHealthMonitor />
      </section>

      {/* Activity Feed */}
      <section>
        <ActivityFeed />
      </section>
    </div>
  );
}