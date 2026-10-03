"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
// import { CheckCircle, XCircle, AlertTriangle, Clock, Server, Users, FileText } from "lucide-react";

// Health check types
type HealthStatus = "healthy" | "degraded" | "error";

interface HealthCheck {
  status: HealthStatus;
  latencyMs: number | null;
  responseTime: "fast" | "normal" | "slow";
  details: {
    [key: string]: any;
  };
  error?: string;
}

interface NetworkHealth {
  status: "operational" | "degraded" | "partial" | "maintenance" | "unknown";
  generatedAt: string;
  checks: {
    database: HealthCheck;
    userService: HealthCheck;
    contributionService: HealthCheck;
  };
  timestamp: string;
}

// Status colors
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

// Health check icon
const getHealthIcon = (status: HealthStatus) => {
  switch (status) {
    case "healthy":
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    case "degraded":
      return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    case "error":
      return <XCircle className="h-4 w-4 text-red-600" />;
  }
};

// Health check label
const getHealthLabel = (status: HealthStatus) => {
  switch (status) {
    case "healthy":
      return "Healthy";
    case "degraded":
      return "Degraded";
    case "error":
      return "Error";
  }
};

// Service icon mapping
const serviceIcons = {
  database: Server,
  userService: Users,
  contributionService: FileText,
};

// Health check card
const HealthCheckCard = ({ name, check }: { name: string; check: HealthCheck }) => {
  const IconComponent = serviceIcons[name as keyof typeof serviceIcons];

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <IconComponent className="h-4 w-4" />
          <span className="font-medium capitalize">{name}</span>
        </div>
        <div className="flex items-center gap-2">
          {getHealthIcon(check.status)}
          <Badge variant={check.status === "healthy" ? "default" : "secondary"}>
            {getHealthLabel(check.status)}
          </Badge>
        </div>
      </div>

      {/* Latency */}
      {check.latencyMs !== null && (
        <div className="text-sm text-gray-600 mb-2">
          Response time: {check.latencyMs}ms ({check.responseTime})
        </div>
      )}

      {/* Details */}
      <div className="space-y-1 text-sm">
        {Object.entries(check.details).map(([key, value]) => (
          <div key={key} className="flex justify-between">
            <span className="text-gray-600 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}:
            </span>
            <span className="font-medium">
              {typeof value === 'number' ? value.toLocaleString() : String(value)}
            </span>
          </div>
        ))}
      </div>

      {/* Error message */}
      {check.error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
          {check.error}
        </div>
      )}
    </Card>
  );
};

export default function NetworkHealthMonitor() {
  const [health, setHealth] = useState<NetworkHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchHealth = async () => {
    try {
      const response = await fetch("/api/network/health");
      const data = await response.json();
      setHealth(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch network health:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Network Health</h2>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <Skeleton className="h-8 w-8 rounded" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-32" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (!health) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Network Health</h2>
        <p className="text-gray-500">Failed to load health data</p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Network Health</h2>
          {lastUpdated && (
            <span className="text-sm text-gray-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>

        <div className="flex items-center gap-4">
          <Badge className={getStatusColor(health.status)}>
            {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
          </Badge>
          <span className="text-sm text-gray-500">
            Generated at {new Date(health.generatedAt).toLocaleString()}
          </span>
        </div>
      </div>

      {/* Service Health Checks */}
      <div className="space-y-4">
        <HealthCheckCard
          name="database"
          check={health.checks.database}
        />

        <HealthCheckCard
          name="userService"
          check={health.checks.userService}
        />

        <HealthCheckCard
          name="contributionService"
          check={health.checks.contributionService}
        />
      </div>

      {/* Health Status Explanations */}
      <div className="mt-6 pt-4 border-t">
        <h3 className="font-medium mb-2">Status Definitions</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="font-medium text-green-600">Operational:</span> All services healthy
          </div>
          <div>
            <span className="font-medium text-yellow-600">Degraded:</span> Some services slow
          </div>
          <div>
            <span className="font-medium text-orange-600">Partial:</span> Non-critical issues
          </div>
          <div>
            <span className="font-medium text-gray-600">Unknown:</span> Health check failed
          </div>
        </div>
      </div>
    </Card>
  );
}