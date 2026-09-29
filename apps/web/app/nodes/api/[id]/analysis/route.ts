import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodes, nodeCapacityHistory, nodeHealth, nodeServiceProofs, nodeEvents } from '@/db/schema';
import { eq, desc, sql, and, gte, lt, avg, max, min, count } from 'drizzle-orm';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const { searchParams } = new URL(request.url);

    // Get time ranges for analysis
    const startTime = searchParams.get('startTime') || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    const endTime = searchParams.get('endTime') || new Date().toISOString();

    // 1. Get basic node information
    const nodeInfo = await db
      .select()
      .from(nodes)
      .where(eq(nodes.id, nodeId))
      .limit(1);

    if (!nodeInfo || nodeInfo.length === 0) {
      return NextResponse.json(
        { error: 'Node not found' },
        { status: 404 }
      );
    }

    const node = nodeInfo[0];

    // 2. Capacity analysis
    const capacityQuery = db.select({
      avgCpuUsage: avg(nodeCapacityHistory.cpuUsagePercent),
      maxCpuUsage: max(nodeCapacityHistory.cpuUsagePercent),
      minCpuUsage: min(nodeCapacityHistory.cpuUsagePercent),
      avgMemoryUsage: avg(nodeCapacityHistory.memoryUsagePercent),
      maxMemoryUsage: max(nodeCapacityHistory.memoryUsagePercent),
      minMemoryUsage: min(nodeCapacityHistory.memoryUsagePercent),
      avgStorageUsage: avg(nodeCapacityHistory.storageUsagePercent),
      maxStorageUsage: max(nodeCapacityHistory.storageUsagePercent),
      avgNetworkIn: avg(nodeCapacityHistory.networkInMbps),
      avgNetworkOut: avg(nodeCapacityHistory.networkOutMbps),
      capacityRecords: count(),
    }).from(nodeCapacityHistory)
      .where(and(
        eq(nodeCapacityHistory.nodeId, nodeId),
        gte(nodeCapacityHistory.recordedAt, startTime),
        lt(nodeCapacityHistory.recordedAt, endTime)
      ));

    const capacityData = await capacityQuery;

    // 3. Health analysis
    const healthQuery = db.select({
      avgHealthScore: avg(nodeHealth.healthScore),
      maxHealthScore: max(nodeHealth.healthScore),
      minHealthScore: min(nodeHealth.healthScore),
      healthyCount: count(),
      degradedCount: count(),
      unhealthyCount: count(),
      lastHealthCheck: max(nodeHealth.checkedAt),
      healthChecks: count(),
    }).from(nodeHealth)
      .where(and(
        eq(nodeHealth.nodeId, nodeId),
        gte(nodeHealth.checkedAt, startTime),
        lt(nodeHealth.checkedAt, endTime)
      ));

    const healthData = await healthQuery;

    // 4. Service proof analysis
    const serviceProofQuery = db.select({
      successfulProofs: count(),
      failedProofs: count(),
      avgVerificationTime: avg(nodeServiceProofs.verificationTimeMs),
      lastProof: max(nodeServiceProofs.createdAt),
    }).from(nodeServiceProofs)
      .where(eq(nodeServiceProofs.nodeId, nodeId));

    const serviceProofData = await serviceProofQuery;

    // 5. Event analysis
    const eventQuery = db.select({
      eventCounts: sql`json_object_agg(
        eventType,
        count(*)
      )`,
      totalEvents: count(),
      lastEvent: max(nodeEvents.timestamp),
    }).from(nodeEvents)
      .where(eq(nodeEvents.nodeId, nodeId));

    const eventData = await eventQuery;

    // 6. Uptime analysis (based on health checks and events)
    const uptimeQuery = db.select({
      uptime: sql`CASE
        WHEN COUNT(*) = 0 THEN 0
        ELSE
          (COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM nodeHealth
            WHERE nodeId = ${nodeId}
              AND checkedAt >= ${startTime}
              AND checkedAt <= ${endTime}
          ))
        END
      ` as uptime,
    }).from(nodeHealth)
      .where(and(
        eq(nodeHealth.nodeId, nodeId),
        gte(nodeHealth.checkedAt, startTime),
        lt(nodeHealth.checkedAt, endTime)
      ));

    const uptimeData = await uptimeQuery;

    // 7. Performance metrics summary
    const performanceQuery = db.select({
      avgLatency: avg(nodeCapacityHistory.networkInMbps),
      maxLatency: max(nodeCapacityHistory.networkInMbps),
      avgLoad: avg(nodeCapacityHistory.loadAvg1),
      maxLoad: max(nodeCapacityHistory.loadAvg1),
      avgTemperature: avg(nodeCapacityHistory.temperature),
    }).from(nodeCapacityHistory)
      .where(and(
        eq(nodeCapacityHistory.nodeId, nodeId),
        gte(nodeCapacityHistory.recordedAt, startTime),
        lt(nodeCapacityHistory.recordedAt, endTime)
      ));

    const performanceData = await performanceQuery;

    // 8. Calculate node score
    let nodeScore = 100; // Start with perfect score

    // Deduct points based on various metrics
    if (capacityData[0]?.maxCpuUsage && capacityData[0].maxCpuUsage > 90) {
      nodeScore -= 10;
    }
    if (capacityData[0]?.maxMemoryUsage && capacityData[0].maxMemoryUsage > 90) {
      nodeScore -= 10;
    }
    if (capacityData[0]?.maxStorageUsage && capacityData[0].maxStorageUsage > 95) {
      nodeScore -= 5;
    }
    if (healthData[0]?.minHealthScore && healthData[0].minHealthScore < 50) {
      nodeScore -= 20;
    }
    if (serviceProofData[0]?.failedProofs && serviceProofData[0].failedProofs > 0) {
      nodeScore -= 15;
    }

    // Ensure score is within 0-100 range
    nodeScore = Math.max(0, Math.min(100, nodeScore));

    // 9. Get recent events
    const recentEvents = await db
      .select({
        id: nodeEvents.id,
        eventType: nodeEvents.eventType,
        timestamp: nodeEvents.timestamp,
        severity: nodeEvents.severity,
        actorType: nodeEvents.actorType,
      })
      .from(nodeEvents)
      .where(eq(nodeEvents.nodeId, nodeId))
      .orderBy(desc(nodeEvents.timestamp))
      .limit(10);

    // 10. Get service trends
    const serviceTrends = await db
      .select({
        date: sql`DATE(timestamp)`,
        totalEvents: count(),
        errorEvents: sql`count(CASE WHEN severity IN ('error', 'critical') THEN 1 END)`,
        warningEvents: sql`count(CASE WHEN severity = 'warning' THEN 1 END)`,
        infoEvents: sql`count(CASE WHEN severity = 'info' THEN 1 END)`,
      })
      .from(nodeEvents)
      .where(and(
        eq(nodeEvents.nodeId, nodeId),
        gte(nodeEvents.timestamp, startTime),
        lt(nodeEvents.timestamp, endTime)
      ))
      .groupBy(sql`DATE(timestamp)`)
      .orderBy(sql`DATE(timestamp)`);

    return NextResponse.json({
      node: node,
      capacity: capacityData[0] || {},
      health: healthData[0] || {},
      serviceProofs: serviceProofData[0] || {},
      events: eventData[0] || {},
      uptime: uptimeData[0] || {},
      performance: performanceData[0] || {},
      nodeScore,
      recentEvents,
      serviceTrends,
      analysisPeriod: {
        startTime,
        endTime,
      },
    });
  } catch (error) {
    console.error('Error fetching node analysis:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Get node health dashboard
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const { dashboardType = 'overview', timeRange = '24h' } = await request.json();

    // Determine time range
    const endTime = new Date();
    let startTime;

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

    // Get basic node info
    const nodeInfo = await db
      .select()
      .from(nodes)
      .where(eq(nodes.id, nodeId))
      .limit(1);

    if (!nodeInfo || nodeInfo.length === 0) {
      return NextResponse.json(
        { error: 'Node not found' },
        { status: 404 }
      );
    }

    const node = nodeInfo[0];

    // Prepare dashboard data based on type
    if (dashboardType === 'health') {
      // Health dashboard
      const healthTrend = await db
        .select({
          timestamp: nodeHealth.checkedAt,
          status: nodeHealth.status,
          healthScore: nodeHealth.healthScore,
          cpuThreshold: nodeHealth.cpuThreshold,
          memoryThreshold: nodeHealth.memoryThreshold,
          recommendations: nodeHealth.recommendations,
        })
        .from(nodeHealth)
        .where(and(
          eq(nodeHealth.nodeId, nodeId),
          gte(nodeHealth.checkedAt, startTime.toISOString()),
          lt(nodeHealth.checkedAt, endTime.toISOString())
        ))
        .orderBy(nodeHealth.checkedAt);

      // Health summary
      const healthSummary = await db.select({
        totalChecks: count(),
        avgHealthScore: avg(nodeHealth.healthScore),
        healthyChecks: count(),
        degradedChecks: count(),
        unhealthyChecks: count(),
      }).from(nodeHealth)
        .where(and(
          eq(nodeHealth.nodeId, nodeId),
          gte(nodeHealth.checkedAt, startTime.toISOString()),
          lt(nodeHealth.checkedAt, endTime.toISOString())
        ));

      return NextResponse.json({
        type: 'health',
        node: node,
        timeRange,
        trend: healthTrend,
        summary: healthSummary[0] || {},
      });

    } else if (dashboardType === 'capacity') {
      // Capacity dashboard
      const capacityTrend = await db
        .select({
          timestamp: nodeCapacityHistory.recordedAt,
          cpuUsage: nodeCapacityHistory.cpuUsagePercent,
          memoryUsage: nodeCapacityHistory.memoryUsagePercent,
          storageUsage: nodeCapacityHistory.storageUsagePercent,
          networkIn: nodeCapacityHistory.networkInMbps,
          networkOut: nodeCapacityHistory.networkOutMbps,
          temperature: nodeCapacityHistory.temperature,
        })
        .from(nodeCapacityHistory)
        .where(and(
          eq(nodeCapacityHistory.nodeId, nodeId),
          gte(nodeCapacityHistory.recordedAt, startTime.toISOString()),
          lt(nodeCapacityHistory.recordedAt, endTime.toISOString())
        ))
        .orderBy(nodeCapacityHistory.recordedAt);

      // Capacity summary
      const capacitySummary = await db.select({
        avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
        avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
        avgStorage: avg(nodeCapacityHistory.storageUsagePercent),
        maxCpu: max(nodeCapacityHistory.cpuUsagePercent),
        maxMemory: max(nodeCapacityHistory.memoryUsagePercent),
        maxStorage: max(nodeCapacityHistory.storageUsagePercent),
      }).from(nodeCapacityHistory)
        .where(and(
          eq(nodeCapacityHistory.nodeId, nodeId),
          gte(nodeCapacityHistory.recordedAt, startTime.toISOString()),
          lt(nodeCapacityHistory.recordedAt, endTime.toISOString())
        ));

      return NextResponse.json({
        type: 'capacity',
        node: node,
        timeRange,
        trend: capacityTrend,
        summary: capacitySummary[0] || {},
      });

    } else {
      // Overview dashboard
      const [health, capacity, events] = await Promise.all([
        // Current health
        db.select().from(nodeHealth)
          .where(eq(nodeHealth.nodeId, nodeId))
          .orderBy(desc(nodeHealth.checkedAt))
          .limit(1),
        // Capacity summary
        db.select({
          avgCpu: avg(nodeCapacityHistory.cpuUsagePercent),
          avgMemory: avg(nodeCapacityHistory.memoryUsagePercent),
          avgNetwork: avg(nodeCapacityHistory.networkInMbps),
        }).from(nodeCapacityHistory)
          .where(and(
            eq(nodeCapacityHistory.nodeId, nodeId),
            gte(nodeCapacityHistory.recordedAt, startTime.toISOString()),
            lt(nodeCapacityHistory.recordedAt, endTime.toISOString())
          ))
          .limit(1),
        // Recent events
        db.select()
          .from(nodeEvents)
          .where(eq(nodeEvents.nodeId, nodeId))
          .orderBy(desc(nodeEvents.timestamp))
          .limit(10)
      ]);

      return NextResponse.json({
        type: 'overview',
        node: node,
        currentHealth: health[0] || null,
        capacitySummary: capacity[0] || {},
        recentEvents: events,
        timeRange,
      });
    }
  } catch (error) {
    console.error('Error fetching node dashboard:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}