import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodes, nodeCapacityHistory, nodeHealth, nodeServiceProofs, nodeEvents } from '@/db/schema';
import { ilike, or, eq, desc, sql, and, avg, max, min, count, gte, lt, inArray } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const dashboardType = searchParams.get('type') || 'overview';

    // Get time range
    const endTime = new Date();
    let startTime: Date;

    const timeRange = searchParams.get('timeRange') || '24h';
    if (timeRange === '1h') {
      startTime = new Date(endTime.getTime() - 60 * 60 * 1000);
    } else if (timeRange === '6h') {
      startTime = new Date(endTime.getTime() - 6 * 60 * 60 * 1000);
    } else if (timeRange === '24h') {
      startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000);
    } else if (timeRange === '7d') {
      startTime = new Date(endTime.getTime() - 7 * 24 * 60 * 60 * 1000);
    } else {
      startTime = new Date(endTime.getTime() - 24 * 60 * 60 * 1000);
    }

    // Generate time range string for queries
    const startTimeStr = startTime.toISOString();
    const endTimeStr = endTime.toISOString();

    // Dashboard data based on type
    switch (dashboardType) {
      case 'overview':
        return await getOverviewDashboard(startTimeStr, endTimeStr);

      case 'health':
        return await getHealthDashboard(startTimeStr, endTimeStr);

      case 'capacity':
        return await getCapacityDashboard(startTimeStr, endTimeStr);

      case 'services':
        return await getServicesDashboard(startTimeStr, endTimeStr);

      case 'events':
        return await getEventsDashboard(startTimeStr, endTimeStr);

      case 'network':
        return await getNetworkDashboard(startTimeStr, endTimeStr);

      default:
        return await getOverviewDashboard(startTimeStr, endTimeStr);
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Overview dashboard
async function getOverviewDashboard(startTime: string, endTime: string) {
  // 1. Node summary
  const nodeSummary = await db
    .select({
      total: count(),
      active: count(),
      draft: count(),
      degraded: count(),
      offline: count(),
      maintenance: count(),
      retired: count(),
      compute: count(),
      ai: count(),
      storage: count(),
      verification: count(),
    })
    .from(nodes);

  const summary = nodeSummary[0] || {};

  // 2. Average health scores by role
  const healthByRole = await db
    .select({
      role: nodes.role,
      avgHealth: avg(nodeHealth.healthScore),
      avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
      avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
      nodeCount: count(),
    })
    .from(nodes)
    .leftJoin(nodeHealth, eq(nodes.id, nodeHealth.nodeId))
    .leftJoin(nodeCapacityHistory, eq(nodes.id, nodeCapacityHistory.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(nodes.role);

  // 3. Recent alerts
  const recentAlerts = await db
    .select({
      id: nodeEvents.id,
      eventType: nodeEvents.eventType,
      severity: nodeEvents.severity,
      timestamp: nodeEvents.timestamp,
      nodeName: nodes.name,
      nodeStatus: nodes.status,
    })
    .from(nodeEvents)
    .leftJoin(nodes, eq(nodeEvents.nodeId, nodes.id))
    .where(and(
      inArray(nodeEvents.eventType, [
        'health_check', 'heartbeat_missed', 'service_proof_failed',
        'alert_triggered', 'status_changed'
      ]),
      gte(nodeEvents.timestamp, startTime),
      lt(nodeEvents.timestamp, endTime)
    ))
    .orderBy(desc(nodeEvents.timestamp))
    .limit(10);

  // 4. Service verification summary
  const serviceSummary = await db
    .select({
      total: count(),
      verified: count(),
      failed: count(),
      avgVerificationTime: avg(nodeServiceProofs.verificationTimeMs),
    })
    .from(nodeServiceProofs)
    .where(and(
      gte(nodeServiceProofs.createdAt, startTime),
      lt(nodeServiceProofs.createdAt, endTime)
    ));

  // 5. Node status distribution
  const statusDistribution = await db
    .select({
      status: nodes.status,
      count: count(),
      avgHealth: avg(nodeHealth.healthScore),
    })
    .from(nodes)
    .leftJoin(nodeHealth, eq(nodes.id, nodeHealth.nodeId))
    .where(gte(nodeHealth.checkedAt, startTime))
    .groupBy(nodes.status);

  // 6. Region distribution
  const regionDistribution = await db
    .select({
      region: nodes.region,
      country: nodes.country,
      count: count(),
      avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, eq(nodes.id, nodeCapacityHistory.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(nodes.region, nodes.country);

  // 7. Resource utilization trends
  const utilizationTrends = await db
    .select({
      date: sql`DATE(timestamp)`,
      avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
      avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
      avgNetwork: avg(nodeCapacityHistory.networkInMbps),
    })
    .from(nodeCapacityHistory)
    .where(and(
      gte(nodeCapacityHistory.timestamp, startTime),
      lt(nodeCapacityHistory.timestamp, endTime)
    ))
    .groupBy(sql`DATE(timestamp)`)
    .orderBy(sql`DATE(timestamp)`);

  // 8. Cloud provider distribution
  const cloudDistribution = await db
    .select({
      cloudProvider: nodes.cloudProvider,
      count: count(),
      hasGPU: sql`count(CASE WHEN hasGPU = true THEN 1 END)`,
    })
    .from(nodes)
    .where(eq(nodes.status, 'active'))
    .groupBy(nodes.cloudProvider);

  return NextResponse.json({
    type: 'overview',
    summary: {
      totalNodes: summary.total || 0,
      activeNodes: summary.active || 0,
      degradedNodes: summary.degraded || 0,
      offlineNodes: summary.offline || 0,
      nodesByRole: {
        compute: summary.compute || 0,
        ai: summary.ai || 0,
        storage: summary.storage || 0,
        verification: summary.verification || 0,
      },
    },
    healthByRole,
    recentAlerts,
    serviceSummary: serviceSummary[0] || {},
    statusDistribution,
    regionDistribution,
    utilizationTrends,
    cloudDistribution,
    timeRange: {
      startTime,
      endTime,
    },
  });
}

// Health dashboard
async function getHealthDashboard(startTime: string, endTime: string) {
  // Get current health status for all nodes
  const currentHealth = await db
    .select({
      node: {
        id: nodes.id,
        name: nodes.name,
        role: nodes.role,
        status: nodes.status,
        hostname: nodes.hostname,
        region: nodes.region,
      },
      health: {
        id: nodeHealth.id,
        status: nodeHealth.status,
        healthScore: nodeHealth.healthScore,
        checkedAt: nodeHealth.checkedAt,
        recommendations: nodeHealth.recommendations,
      },
    })
    .from(nodes)
    .leftJoin(nodeHealth, and(
      eq(nodes.id, nodeHealth.nodeId),
      eq(nodeHealth.checkedAt, sql`(SELECT MAX(checkedAt) FROM nodeHealth WHERE nodeId = nodes.id)`)
    ))
    .where(eq(nodes.status, 'active'));

  // Health trend data
  const healthTrends = await db
    .select({
      date: sql`DATE(checkedAt)`,
      healthy: count(),
      degraded: count(),
      unhealthy: count(),
      avgHealthScore: avg(nodeHealth.healthScore),
    })
    .from(nodeHealth)
    .where(and(
      gte(nodeHealth.checkedAt, startTime),
      lt(nodeHealth.checkedAt, endTime)
    ))
    .groupBy(sql`DATE(checkedAt)`)
    .orderBy(sql`DATE(checkedAt)`);

  // Health alerts by severity
  const healthAlerts = await db
    .select({
      severity: nodeEvents.severity,
      count: count(),
      eventTypes: sql`json_group_array(DISTINCT eventType)`,
    })
    .from(nodeEvents)
    .where(and(
      inArray(nodeEvents.eventType, [
        'health_check', 'heartbeat_missed', 'alert_triggered'
      ]),
      gte(nodeEvents.timestamp, startTime),
      lt(nodeEvents.timestamp, endTime)
    ))
    .groupBy(nodeEvents.severity);

  // Service availability by region
  const serviceAvailability = await db
    .select({
      region: nodes.region,
      country: nodes.country,
      availability: sql`avg(CASE WHEN health.healthScore >= 80 THEN 100 ELSE health.healthScore END)`,
    })
    .from(nodes)
    .leftJoin(nodeHealth, eq(nodes.id, nodeHealth.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeHealth.checkedAt, startTime),
      lt(nodeHealth.checkedAt, endTime)
    ))
    .groupBy(nodes.region, nodes.country);

  return NextResponse.json({
    type: 'health',
    currentHealth,
    healthTrends,
    healthAlerts,
    serviceAvailability,
    timeRange: {
      startTime,
      endTime,
    },
  });
}

// Capacity dashboard
async function getCapacityDashboard(startTime: string, endTime: string) {
  // Get current capacity for active nodes
  const currentCapacity = await db
    .select({
      node: {
        id: nodes.id,
        name: nodes.name,
        role: nodes.role,
        hostname: nodes.hostname,
        region: nodes.region,
      },
      capacity: {
        cpuUsage: nodeCapacityHistory.cpuUsagePercent,
        memoryUsage: nodeCapacityHistory.memoryUsagePercent,
        storageUsage: nodeCapacityHistory.storageUsagePercent,
        networkIn: nodeCapacityHistory.networkInMbps,
        networkOut: nodeCapacityHistory.networkOutMbps,
        temperature: nodeCapacityHistory.temperature,
        recordedAt: nodeCapacityHistory.recordedAt,
      },
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, and(
      eq(nodes.id, nodeCapacityHistory.nodeId),
      eq(nodeCapacityHistory.recordedAt, sql`(SELECT MAX(recordedAt) FROM nodeCapacityHistory WHERE nodeId = nodes.id)`)
    ))
    .where(eq(nodes.status, 'active'));

  // Capacity trends by resource type
  const capacityTrends = await db
    .select({
      date: sql`DATE(recordedAt)`,
      avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
      avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
      avgStorage: avg(nodeCapacityHistory.storageUsagePercent),
      avgNetwork: avg(nodeCapacityHistory.networkInMbps),
    })
    .from(nodeCapacityHistory)
    .where(and(
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(sql`DATE(recordedAt)`)
    .orderBy(sql`DATE(recordedAt)`);

  // Resource utilization by role
  const utilizationByRole = await db
    .select({
      role: nodes.role,
      avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
      avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
      avgStorage: avg(nodeCapacityHistory.storageUsagePercent),
      avgNetwork: avg(nodeCapacityHistory.networkInMbps),
      maxCpu: max(nodeCapacityHistory.cpuUsagePercent),
      maxMemory: max(nodeCapacityHistory.memoryUsagePercent),
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, eq(nodes.id, nodeCapacityHistory.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(nodes.role);

  // Nodes near capacity thresholds
  const nearThreshold = await db
    .select({
      node: {
        id: nodes.id,
        name: nodes.name,
        role: nodes.role,
        hostname: nodes.hostname,
        region: nodes.region,
      },
      capacity: {
        cpuUsage: nodeCapacityHistory.cpuUsagePercent,
        memoryUsage: nodeCapacityHistory.memoryUsagePercent,
        recordedAt: nodeCapacityHistory.recordedAt,
      },
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, and(
      eq(nodes.id, nodeCapacityHistory.nodeId),
      gt(nodeCapacityHistory.cpuUsagePercent, 80),
      gt(nodeCapacityHistory.memoryUsagePercent, 80)
    ))
    .where(eq(nodes.status, 'active'));

  return NextResponse.json({
    type: 'capacity',
    currentCapacity,
    capacityTrends,
    utilizationByRole,
    nearThreshold,
    timeRange: {
      startTime,
      endTime,
    },
  });
}

// Services dashboard
async function getServicesDashboard(startTime: string, endTime: string) {
  // Service verification status
  const verificationStatus = await db
    .select({
      status: nodeServiceProofs.status,
      count: count(),
      avgVerificationTime: avg(nodeServiceProofs.verificationTimeMs),
    })
    .from(nodeServiceProofs)
    .where(gte(nodeServiceProofs.createdAt, startTime))
    .groupBy(nodeServiceProofs.status);

  // Verification trends
  const verificationTrends = await db
    .select({
      date: sql`DATE(createdAt)`,
      verified: count(),
      failed: count(),
      avgTime: avg(nodeServiceProofs.verificationTimeMs),
    })
    .from(nodeServiceProofs)
    .where(and(
      gte(nodeServiceProofs.createdAt, startTime),
      lt(nodeServiceProofs.createdAt, endTime)
    ))
    .groupBy(sql`DATE(createdAt)`)
    .orderBy(sql`DATE(createdAt)`);

  // Service failures by type
  const serviceFailures = await db
    .select({
      failureReason: nodeServiceProofs.failureReason,
      count: count(),
      avgTime: avg(nodeServiceProofs.verificationTimeMs),
    })
    .from(nodeServiceProofs)
    .where(and(
      eq(nodeServiceProofs.status, 'failed'),
      gte(nodeServiceProofs.createdAt, startTime),
      lt(nodeServiceProofs.createdAt, endTime)
    ))
    .groupBy(nodeServiceProofs.failureReason);

  // Success rate by region
  const successRateByRegion = await db
    .select({
      region: nodes.region,
      country: nodes.country,
      successRate: sql`count(CASE WHEN sp.status = 'verified' THEN 1 END) * 100.0 / count(*)`,
      totalChecks: count(),
    })
    .from(nodes)
    .leftJoin(nodeServiceProofs, eq(nodes.id, nodeServiceProofs.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeServiceProofs.createdAt, startTime),
      lt(nodeServiceProofs.createdAt, endTime)
    ))
    .groupBy(nodes.region, nodes.country);

  // Recent service events
  const recentServiceEvents = await db
    .select({
      eventType: nodeEvents.eventType,
      timestamp: nodeEvents.timestamp,
      severity: nodeEvents.severity,
      nodeName: nodes.name,
      nodeRole: nodes.role,
    })
    .from(nodeEvents)
    .leftJoin(nodes, eq(nodeEvents.nodeId, nodes.id))
    .where(and(
      inArray(nodeEvents.eventType, [
        'service_proof_created', 'service_proof_verified', 'service_proof_failed'
      ]),
      gte(nodeEvents.timestamp, startTime),
      lt(nodeEvents.timestamp, endTime)
    ))
    .orderBy(desc(nodeEvents.timestamp))
    .limit(20);

  return NextResponse.json({
    type: 'services',
    verificationStatus,
    verificationTrends,
    serviceFailures,
    successRateByRegion,
    recentServiceEvents,
    timeRange: {
      startTime,
      endTime,
    },
  });
}

// Network dashboard
async function getNetworkDashboard(startTime: string, endTime: string) {
  // Network latency by region
  const networkLatency = await db
    .select({
      region: nodes.region,
      country: nodes.country,
      avgLatency: avg(nodeCapacityHistory.networkInMbps),
      maxLatency: max(nodeCapacityHistory.networkInMbps),
      minLatency: min(nodeCapacityHistory.networkInMbps),
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, eq(nodes.id, nodeCapacityHistory.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(nodes.region, nodes.country);

  // Bandwidth utilization
  const bandwidthUtilization = await db
    .select({
      date: sql`DATE(recordedAt)`,
      avgInbound: avg(nodeCapacityHistory.networkInMbps),
      avgOutbound: avg(nodeCapacityHistory.networkOutMbps),
      peakInbound: max(nodeCapacityHistory.networkInMbps),
      peakOutbound: max(nodeCapacityHistory.networkOutMbps),
    })
    .from(nodeCapacityHistory)
    .where(gte(nodeCapacityHistory.recordedAt, startTime))
    .groupBy(sql`DATE(recordedAt)`)
    .orderBy(sql`DATE(recordedAt)`);

  // Network errors
  const networkErrors = await db
    .select({
      errorType: nodeEvents.eventType,
      count: count(),
      severity: nodeEvents.severity,
    })
    .from(nodeEvents)
    .where(and(
      inArray(nodeEvents.eventType, ['network_error', 'connection_failed', 'timeout']),
      gte(nodeEvents.timestamp, startTime),
      lt(nodeEvents.timestamp, endTime)
    ))
    .groupBy(nodeEvents.eventType, nodeEvents.severity);

  // Cross-region latency
  const crossRegionLatency = await db
    .select({
      sourceRegion: nodes.region,
      avgCrossRegion: sql`avg(network.crossRegionLatencyMs)`,
    })
    .from(nodes)
    .leftJoin(nodeCapacityHistory, eq(nodes.id, nodeCapacityHistory.nodeId))
    .where(and(
      eq(nodes.status, 'active'),
      gte(nodeCapacityHistory.recordedAt, startTime),
      lt(nodeCapacityHistory.recordedAt, endTime)
    ))
    .groupBy(nodes.region);

  return NextResponse.json({
    type: 'network',
    networkLatency,
    bandwidthUtilization,
    networkErrors,
    crossRegionLatency,
    timeRange: {
      startTime,
      endTime,
    },
  });
}

// Events dashboard
async function getEventsDashboard(startTime: string, endTime: string) {
  // Event distribution by type
  const eventTypeDistribution = await db
    .select({
      eventType: nodeEvents.eventType,
      count: count(),
      severity: nodeEvents.severity,
    })
    .from(nodeEvents)
    .where(gte(nodeEvents.timestamp, startTime))
    .groupBy(nodeEvents.eventType, nodeEvents.severity)
    .orderBy(sql`count(*) DESC`);

  // Event timeline
  const eventTimeline = await db
    .select({
      timestamp: nodeEvents.timestamp,
      eventType: nodeEvents.eventType,
      severity: nodeEvents.severity,
      nodeName: nodes.name,
      nodeRole: nodes.role,
    })
    .from(nodeEvents)
    .leftJoin(nodes, eq(nodeEvents.nodeId, nodes.id))
    .where(gte(nodeEvents.timestamp, startTime))
    .orderBy(desc(nodeEvents.timestamp))
    .limit(50);

  // Event frequency by hour
  const eventFrequency = await db
    .select({
      hour: sql`extract(hour from timestamp)`,
      count: count(),
      eventType: nodeEvents.eventType,
    })
    .from(nodeEvents)
    .where(gte(nodeEvents.timestamp, startTime))
    .groupBy(sql`extract(hour from timestamp)`, nodeEvents.eventType)
    .orderBy(sql`extract(hour from timestamp)`, nodeEvents.eventType);

  // Alert summary
  const alertSummary = await db
    .select({
      severity: nodeEvents.severity,
      count: count(),
      criticalAlerts: sql`count(CASE WHEN severity = 'critical' THEN 1 END)`,
    })
    .from(nodeEvents)
    .where(and(
      inArray(nodeEvents.eventType, ['alert_triggered', 'critical_error']),
      gte(nodeEvents.timestamp, startTime),
      lt(nodeEvents.timestamp, endTime)
    ))
    .groupBy(nodeEvents.severity);

  // Node activity
  const nodeActivity = await db
    .select({
      nodeId: nodeEvents.nodeId,
      nodeName: nodes.name,
      nodeRole: nodes.role,
      eventCount: count(),
      lastEvent: max(nodeEvents.timestamp),
    })
    .from(nodeEvents)
    .leftJoin(nodes, eq(nodeEvents.nodeId, nodes.id))
    .where(gte(nodeEvents.timestamp, startTime))
    .groupBy(nodeEvents.nodeId, nodes.name, nodes.role)
    .orderBy(sql`eventCount DESC`)
    .limit(20);

  return NextResponse.json({
    type: 'events',
    eventTypeDistribution,
    eventTimeline,
    eventFrequency,
    alertSummary,
    nodeActivity,
    timeRange: {
      startTime,
      endTime,
    },
  });
}