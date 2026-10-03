import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
  Security,
  Search,
  Filter,
  Grid,
  List
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

interface DashboardData {
  type: string;
  summary: any;
  healthByRole: any[];
  recentAlerts: any[];
  serviceSummary: any;
  statusDistribution: any[];
  regionDistribution: any[];
  utilizationTrends: any[];
  cloudDistribution: any[];
  timeRange: any;
}

export default function NodeRegistryDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState('overview');

  const fetchDashboardData = async () => {
    try {
      const res = await fetch('/nodes/dashboard?type=overview&timeRange=24h');
      const data = await res.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchNodes = async () => {
    try {
      const res = await fetch('/nodes');
      const data = await res.json();
      setNodes(data.nodes || []);
    } catch (error) {
      console.error('Error fetching nodes:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDashboardData(), fetchNodes()]);
      setLoading(false);
    };
    loadData();
  }, []);

  const filteredNodes = nodes.filter(node => {
    const matchesSearch = node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         node.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         node.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesRole = filterRole === 'all' || node.role === filterRole;
    const matchesStatus = filterStatus === 'all' || node.status === filterStatus;
    return matchesSearch && matchesRole && matchesStatus;
  });

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
      case 'compute': return <Monitor className="h-4 w-4" />;
      case 'ai': return <Brain className="h-4 w-4" />;
      case 'storage': return <HardDrive className="h-4 w-4" />;
      case 'verification': return <Shield className="h-4 w-4" />;
      default: return <Server className="h-4 w-4" />;
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Node Registry Dashboard</h1>
        <Button onClick={fetchDashboardData} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Quick Stats */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Nodes</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.summary.totalNodes || 0}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.summary.activeNodes || 0} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Degraded Nodes</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.summary.degradedNodes || 0}</div>
              <p className="text-xs text-muted-foreground">Needs attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Offline Nodes</CardTitle>
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.summary.offlineNodes || 0}</div>
              <p className="text-xs text-muted-foreground">Unresponsive</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Service Uptime</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">99.9%</div>
              <Progress value={99.9} className="mt-2" />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="nodes">Nodes</TabsTrigger>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="capacity">Capacity</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="events">Events</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {dashboardData && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Nodes by Role */}
                <Card>
                  <CardHeader>
                    <CardTitle>Nodes by Role</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {Object.entries(dashboardData.summary.nodesByRole || {}).map(([role, count]) => (
                      <div key={role} className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          {getRoleIcon(role as any)}
                          <span className="capitalize">{role}</span>
                        </div>
                        <Badge className={getRoleColor(role as any)}>
                          {count}
                        </Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Recent Alerts */}
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Alerts</CardTitle>
                    <CardDescription>Last 24 hours</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {dashboardData.recentAlerts?.length > 0 ? (
                      <div className="space-y-2">
                        {dashboardData.recentAlerts.slice(0, 5).map((alert: any) => (
                          <div key={alert.id} className="flex items-center justify-between p-2 rounded border">
                            <div className="flex items-center gap-2">
                              {alert.severity === 'critical' ? (
                                <XCircle className="h-4 w-4 text-red-500" />
                              ) : (
                                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                              )}
                              <span className="text-sm">{alert.eventType}</span>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {new Date(alert.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No recent alerts</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Utilization Trends */}
              <Card>
                <CardHeader>
                  <CardTitle>Resource Utilization Trends</CardTitle>
                  <CardDescription>24-hour averages</CardDescription>
                </CardHeader>
                <CardContent>
                  {dashboardData.utilizationTrends?.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {['avgCpu', 'avgMemory', 'avgNetwork'].map((metric, index) => {
                        const values = dashboardData.utilizationTrends
                          .map(t => t[metric] || 0)
                          .filter(v => v > 0);
                        const avgValue = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;

                        return (
                          <div key={metric}>
                            <label className="text-sm font-medium capitalize">
                              {metric.replace('avg', '').replace(/([A-Z])/g, ' $1').trim()}
                            </label>
                            <div className="mt-1">
                              <Progress value={avgValue} />
                              <p className="text-sm text-muted-foreground mt-1">
                                {avgValue.toFixed(1)}%
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No utilization data available</p>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="nodes" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search nodes..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                <Select value={filterRole} onValueChange={setFilterRole}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Roles</SelectItem>
                    <SelectItem value="compute">Compute</SelectItem>
                    <SelectItem value="ai">AI</SelectItem>
                    <SelectItem value="storage">Storage</SelectItem>
                    <SelectItem value="verification">Verification</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="degraded">Degraded</SelectItem>
                    <SelectItem value="offline">Offline</SelectItem>
                    <SelectItem value="maintenance">Maintenance</SelectItem>
                    <SelectItem value="retired">Retired</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSearchQuery('');
                    setFilterRole('all');
                    setFilterStatus('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">
              Showing {filteredNodes.length} of {nodes.length} nodes
            </p>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Node Grid */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredNodes.map(node => (
                <Card key={node.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        {getRoleIcon(node.role)}
                        <CardTitle className="text-lg">{node.name}</CardTitle>
                      </div>
                      <Badge className={getStatusColor(node.status)}>
                        {node.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-sm text-muted-foreground">{node.description}</p>
                    <div className="flex justify-between text-sm">
                      <span className="flex items-center gap-1">
                        <Monitor className="h-3 w-3" />
                        {node.cpuCores} CPU
                      </span>
                      <span className="flex items-center gap-1">
                        <HardDrive className="h-3 w-3" />
                        {node.memoryGB} GB RAM
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {node.region}
                      </span>
                      <span className="flex items-center gap-1">
                        <Activity className="h-3 w-3" />
                        {node.lastHeartbeatAt ? 'Online' : 'Offline'}
                      </span>
                    </div>
                    <div className="flex gap-1">
                      <Badge variant="secondary" className="text-xs">
                        {node.role}
                      </Badge>
                      {node.hasGPU && (
                        <Badge variant="secondary" className="text-xs">
                          GPU
                        </Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            /* Node List */
            <div className="space-y-2">
              {filteredNodes.map(node => (
                <Card key={node.id}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          {getRoleIcon(node.role)}
                          <span className="font-medium">{node.name}</span>
                        </div>
                        <Badge className={getRoleColor(node.role)}>
                          {node.role}
                        </Badge>
                        <Badge className={getStatusColor(node.status)}>
                          {node.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm">{node.region}</span>
                        <span className="text-sm">{node.city}</span>
                        <Button variant="outline" size="sm">
                          View
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {filteredNodes.length === 0 && (
            <Alert>
              <Search className="h-4 w-4" />
              <AlertDescription>
                No nodes found matching your filters.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        <TabsContent value="health" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Health Overview</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.healthByRole?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {dashboardData.healthByRole.map((roleHealth: any) => (
                    <Card key={roleHealth.role}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          {getRoleIcon(roleHealth.role)}
                          <span className="capitalize">{roleHealth.role} Nodes</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div>
                            <label className="text-sm font-medium">Average Health Score</label>
                            <div className="mt-1">
                              <Progress value={roleHealth.avgHealth || 0} />
                              <p className="text-sm text-muted-foreground mt-1">
                                {roleHealth.avgHealth || 0}%
                              </p>
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="text-sm font-medium">Avg CPU Usage</label>
                              <p className="text-lg font-semibold mt-1">
                                {roleHealth.avgCpu?.toFixed(1) || 0}%
                              </p>
                            </div>
                            <div>
                              <label className="text-sm font-medium">Avg Memory Usage</label>
                              <p className="text-lg font-semibold mt-1">
                                {roleHealth.avgMemory?.toFixed(1) || 0}%
                              </p>
                            </div>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {roleHealth.nodeCount} nodes in this role
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No health data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="capacity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Capacity Management</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.utilizationByRole?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.utilizationByRole.map((roleData: any) => (
                    <Card key={roleData.role}>
                      <CardHeader>
                        <CardTitle className="capitalize">{roleData.role} Nodes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <label className="text-sm font-medium">Avg CPU</label>
                            <p className="text-lg font-semibold mt-1">
                              {roleData.avgCpu?.toFixed(1) || 0}%
                            </p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Max CPU</label>
                            <p className="text-lg font-semibold mt-1">
                              {roleData.maxCpu?.toFixed(1) || 0}%
                            </p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Avg Memory</label>
                            <p className="text-lg font-semibold mt-1">
                              {roleData.avgMemory?.toFixed(1) || 0}%
                            </p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Max Memory</label>
                            <p className="text-lg font-semibold mt-1">
                              {roleData.maxMemory?.toFixed(1) || 0}%
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No capacity data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Verification</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.serviceSummary ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium">Total Checks</label>
                    <p className="text-2xl font-bold mt-1">
                      {dashboardData.serviceSummary.total || 0}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Verified</label>
                    <p className="text-2xl font-bold mt-1 text-green-600">
                      {dashboardData.serviceSummary.verified || 0}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Avg Verification Time</label>
                    <p className="text-2xl font-bold mt-1">
                      {dashboardData.serviceSummary.avgVerificationTime || 0}ms
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">No service verification data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Events</CardTitle>
            </CardHeader>
            <CardContent>
              {dashboardData?.recentAlerts?.length > 0 ? (
                <div className="space-y-3">
                  {dashboardData.recentAlerts.map((event: any) => (
                    <div key={event.id} className="flex items-center justify-between p-3 rounded border">
                      <div className="flex items-center gap-3">
                        {event.severity === 'critical' ? (
                          <XCircle className="h-5 w-5 text-red-500" />
                        ) : (
                          <AlertTriangle className="h-5 w-5 text-yellow-500" />
                        )}
                        <div>
                          <p className="font-medium">{event.eventType}</p>
                          <p className="text-sm text-muted-foreground">Node: {event.nodeName}</p>
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No recent events</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}