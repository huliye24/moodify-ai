import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Server,
  Activity,
  Heart,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  MapPin,
  Monitor,
  HardDrive,
  Zap,
  Shield,
  Globe,
  BarChart3,
  TrendingUp,
  Clock,
  Wifi,
  Database,
  Brain,
  Security
} from 'lucide-react';

interface Node {
  id: string;
  slug: string;
  name: string;
  description: string;
  role: 'compute' | 'ai' | 'storage' | 'verification';
  status: 'draft' | 'active' | 'degraded' | 'offline' | 'maintenance' | 'retired';
  cloudProvider?: string;
  region?: string;
  availabilityZone?: string;
  hostname?: string;
  cpuCores?: number;
  memoryGB?: number;
  storageGB?: number;
  bandwidthMbps?: number;
  hasGPU?: boolean;
  gpuCount?: number;
  gpuModel?: string;
  country?: string;
  city?: string;
  latitude?: string;
  longitude?: string;
  operatorType?: 'resident' | 'organization';
  operatorResidentId?: string;
  operatorOrganizationId?: string;
  createdAt: string;
  updatedAt: string;
  lastHeartbeatAt?: string;
  tags: string[];
  metadata?: Record<string, any>;
}

interface NodeOverviewProps {
  node: Node;
  onUpdate?: (node: Node) => void;
  onRefresh?: () => void;
}

export default function NodeOverview({ node, onUpdate, onRefresh }: NodeOverviewProps) {
  const [health, setHealth] = useState<any>(null);
  const [capacity, setCapacity] = useState<any>(null);
  const [score, setScore] = useState<number>(100);
  const [loading, setLoading] = useState(false);

  const fetchNodeData = async () => {
    setLoading(true);
    try {
      // Fetch health data
      const healthRes = await fetch(`/nodes/${node.id}/health`);
      const healthData = await healthRes.json();
      setHealth(healthRes.ok ? healthData : null);

      // Fetch capacity data
      const capacityRes = await fetch(`/nodes/${node.id}/capacity`);
      const capacityData = await capacityRes.json();
      setCapacity(capacityRes.ok ? capacityData : []);

      // Calculate score based on data
      if (healthRes.ok) {
        let calculatedScore = 100;
        if (health.status === 'degraded') calculatedScore -= 20;
        if (health.status === 'unhealthy') calculatedScore -= 40;
        if (capacity.length > 0) {
          const latestCapacity = capacity[0];
          if (latestCapacity.cpuUsagePercent > 90) calculatedScore -= 10;
          if (latestCapacity.memoryUsagePercent > 90) calculatedScore -= 10;
        }
        setScore(Math.max(0, calculatedScore));
      }
    } catch (error) {
      console.error('Error fetching node data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodeData();
  }, [node.id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      case 'maintenance': return 'bg-blue-500';
      case 'retired': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'compute': return <Monitor className="h-5 w-5" />;
      case 'ai': return <Brain className="h-5 w-5" />;
      case 'storage': return <HardDrive className="h-5 w-5" />;
      case 'verification': return <Shield className="h-5 w-5" />;
      default: return <Server className="h-5 w-5" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'compute': return 'bg-purple-100 text-purple-800';
      case 'ai': return 'bg-pink-100 text-pink-800';
      case 'storage': return 'bg-blue-100 text-blue-800';
      case 'verification': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {getRoleIcon(node.role)}
            <h1 className="text-2xl font-bold">{node.name}</h1>
          </div>
          <Badge className={getRoleColor(node.role)}>
            {node.role}
          </Badge>
          <Badge className={getStatusColor(node.status)}>
            {node.status}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          {onUpdate && (
            <Button
              size="sm"
              onClick={() => onUpdate(node)}
            >
              Edit
            </Button>
          )}
        </div>
      </div>

      {/* Score and Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Node Score</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{score}</div>
            <Progress value={score} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Heartbeat</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {node.lastHeartbeatAt ? (
              <div className="text-2xl font-bold">
                {new Date(node.lastHeartbeatAt).toLocaleString()}
              </div>
            ) : (
              <div className="text-2xl font-bold text-red-500">Unknown</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Location</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {node.city}, {node.country}
            </div>
            <p className="text-xs text-muted-foreground">
              {node.region} • {node.availabilityZone}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Details Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="capacity">Capacity</TabsTrigger>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Compute Resources
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span>CPU Cores</span>
                  <span className="font-medium">{node.cpuCores}</span>
                </div>
                <div className="flex justify-between">
                  <span>Memory</span>
                  <span className="font-medium">{node.memoryGB} GB</span>
                </div>
                <div className="flex justify-between">
                  <span>Storage</span>
                  <span className="font-medium">{node.storageGB} GB</span>
                </div>
                <div className="flex justify-between">
                  <span>Bandwidth</span>
                  <span className="font-medium">{node.bandwidthMbps} Mbps</span>
                </div>
                <div className="flex justify-between">
                  <span>GPU</span>
                  <span className="font-medium">
                    {node.hasGPU ? `${node.gpuCount} ${node.gpuModel}` : 'No'}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Infrastructure Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span>Cloud Provider</span>
                  <span className="font-medium">{node.cloudProvider || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Region</span>
                  <span className="font-medium">{node.region || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Availability Zone</span>
                  <span className="font-medium">{node.availabilityZone || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Hostname</span>
                  <span className="font-medium">{node.hostname || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Coordinates</span>
                  <span className="font-medium">
                    {node.latitude && node.longitude ? `${node.latitude}, ${node.longitude}` : 'Unknown'}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Security className="h-5 w-5" />
                  Identity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span>Stable ID</span>
                  <span className="font-medium font-mono text-xs">
                    {node.stableId ? node.stableId.substring(0, 8) + '...' : 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Operator Type</span>
                  <span className="font-medium">{node.operatorType || 'None'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Created</span>
                  <span className="font-medium">
                    {new Date(node.createdAt).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Updated</span>
                  <span className="font-medium">
                    {new Date(node.updatedAt).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Tags
                </CardTitle>
              </CardHeader>
              <CardContent>
                {node.tags.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {node.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No tags assigned</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="capacity" className="space-y-4">
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <RefreshCw className="h-6 w-6 animate-spin" />
              <span className="ml-2">Loading capacity data...</span>
            </div>
          ) : capacity.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Current Capacity</CardTitle>
                <CardDescription>
                  Latest resource usage metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="text-sm font-medium">CPU Usage</label>
                    <div className="mt-1">
                      <Progress value={capacity[0].cpuUsagePercent} />
                      <p className="text-sm text-muted-foreground mt-1">
                        {capacity[0].cpuUsagePercent}%
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Memory Usage</label>
                    <div className="mt-1">
                      <Progress value={capacity[0].memoryUsagePercent} />
                      <p className="text-sm text-muted-foreground mt-1">
                        {capacity[0].memoryUsagePercent}%
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Storage Usage</label>
                    <div className="mt-1">
                      <Progress value={capacity[0].storageUsagePercent} />
                      <p className="text-sm text-muted-foreground mt-1">
                        {capacity[0].storageUsagePercent}%
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Network In</label>
                    <p className="text-2xl font-bold mt-1">
                      {capacity[0].networkInMbps} Mbps
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                No capacity data available for this node
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="health" className="space-y-4">
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <RefreshCw className="h-6 w-6 animate-spin" />
              <span className="ml-2">Loading health data...</span>
            </div>
          ) : health ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {health.status === 'healthy' ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : health.status === 'degraded' ? (
                    <AlertTriangle className="h-5 w-5 text-yellow-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  Health Status
                </CardTitle>
                <CardDescription>
                  Last checked: {new Date(health.checkedAt).toLocaleString()}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium">Health Score</label>
                    <div className="mt-1">
                      <Progress value={health.healthScore} />
                      <p className="text-sm text-muted-foreground mt-1">
                        {health.healthScore}%
                      </p>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Latency</label>
                    <p className="text-lg font-semibold mt-1">
                      {health.apiLatencyMs || 0}ms
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Services</label>
                    <p className="text-lg font-semibold mt-1">
                      {health.servicesAvailable ? 'Available' : 'Unavailable'}
                    </p>
                  </div>
                </div>

                {health.recommendations && health.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Recommendations</h4>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {health.recommendations.map((rec: string, index: number) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                No health data available for this node
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wifi className="h-5 w-5" />
                Network Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              {node.cloudProvider && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Cloud Provider</label>
                    <p className="text-lg font-semibold mt-1">{node.cloudProvider}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Region</label>
                    <p className="text-lg font-semibold mt-1">{node.region}</p>
                  </div>
                </div>
              )}
              <p className="text-sm text-muted-foreground mt-4">
                Network monitoring data will be displayed here once the node starts reporting
                network metrics.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}