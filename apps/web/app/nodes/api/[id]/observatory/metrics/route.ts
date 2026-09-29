import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodeObservatoryMetrics } from '@/db/schema';
import { eq, desc, sql, and, gte, lt } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateObservatoryMetricsPayload {
  timestamp: string;
  networkLatencyMs?: number;
  packetLossPercent?: number;
  jitterMs?: number;
  bandwidthMbps?: number;
  throughputBps?: number;
  dnsResolutionTimeMs?: number;
  tcpConnectionTimeMs?: number;
  httpResponseTimeMs?: number;
  tcpConnectionFailures?: number;
  networkErrors?: number;
  availabilityScore?: number;
  uptimePercent?: number;
  failedHealthChecks?: number;
  successfulHealthChecks?: number;
  dataCenterLatencyMs?: number;
  crossRegionLatencyMs?: number;
  blockchainSyncDelay?: number;
  encryptionOverheadMs?: number;
  metadata?: Record<string, any>;
}

// Helper function to get time ranges
function getTimeRange(start: string, end: string): { gte: string, lt: string } {
  return {
    gte: start,
    lt: end,
  };
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const { searchParams } = new URL(request.url);

    // Extract query parameters
    const startTime = searchParams.get('startTime');
    const endTime = searchParams.get('endTime');
    const timeRange = searchParams.get('timeRange'); // '1h', '6h', '24h', '7d', '30d'
    const metricType = searchParams.get('metricType');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '1000'), 1000);
    const offset = (page - 1) * limit;
    const sortBy = searchParams.get('sortBy') || 'timestamp';
    const sortOrder = searchParams.get('sortOrder') || 'desc';

    // Set default time range if not provided
    let defaultStartTime;
    if (timeRange === '1h') {
      defaultStartTime = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    } else if (timeRange === '6h') {
      defaultStartTime = new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString();
    } else if (timeRange === '24h') {
      defaultStartTime = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    } else if (timeRange === '7d') {
      defaultStartTime = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
    } else if (timeRange === '30d') {
      defaultStartTime = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
    } else {
      defaultStartTime = startTime || new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    }

    const actualStartTime = startTime || defaultStartTime;
    const actualEndTime = endTime || new Date().toISOString();

    // Build query conditions
    const whereConditions = [
      eq(nodeObservatoryMetrics.nodeId, nodeId),
      gte(nodeObservatoryMetrics.timestamp, actualStartTime),
      lt(nodeObservatoryMetrics.timestamp, actualEndTime)
    ];

    if (metricType) {
      // Check if metricType is in the specific fields
      const metricFields = [
        'networkLatencyMs',
        'packetLossPercent',
        'jitterMs',
        'bandwidthMbps',
        'throughputBps',
        'dnsResolutionTimeMs',
        'tcpConnectionTimeMs',
        'httpResponseTimeMs',
        'tcpConnectionFailures',
        'networkErrors',
        'availabilityScore',
        'uptimePercent',
        'failedHealthChecks',
        'successfulHealthChecks',
        'dataCenterLatencyMs',
        'crossRegionLatencyMs',
        'blockchainSyncDelay',
        'encryptionOverheadMs'
      ];

      // Create OR condition for metric type matching
      const metricConditions = metricFields.map(field =>
        sql`${nodeObservatoryMetrics[field]} IS NOT NULL`
      );

      whereConditions.push(or(...metricConditions));
    }

    // Build query
    const query = db.select({
      id: nodeObservatoryMetrics.id,
      nodeId: nodeObservatoryMetrics.nodeId,
      timestamp: nodeObservatoryMetrics.timestamp,
      networkLatencyMs: nodeObservatoryMetrics.networkLatencyMs,
      packetLossPercent: nodeObservatoryMetrics.packetLossPercent,
      jitterMs: nodeObservatoryMetrics.jitterMs,
      bandwidthMbps: nodeObservatoryMetrics.bandwidthMbps,
      throughputBps: nodeObservatoryMetrics.throughputBps,
      dnsResolutionTimeMs: nodeObservatoryMetrics.dnsResolutionTimeMs,
      tcpConnectionTimeMs: nodeObservatoryMetrics.tcpConnectionTimeMs,
      httpResponseTimeMs: nodeObservatoryMetrics.httpResponseTimeMs,
      tcpConnectionFailures: nodeObservatoryMetrics.tcpConnectionFailures,
      networkErrors: nodeObservatoryMetrics.networkErrors,
      availabilityScore: nodeObservatoryMetrics.availabilityScore,
      uptimePercent: nodeObservatoryMetrics.uptimePercent,
      failedHealthChecks: nodeObservatoryMetrics.failedHealthChecks,
      successfulHealthChecks: nodeObservatoryMetrics.successfulHealthChecks,
      dataCenterLatencyMs: nodeObservatoryMetrics.dataCenterLatencyMs,
      crossRegionLatencyMs: nodeObservatoryMetrics.crossRegionLatencyMs,
      blockchainSyncDelay: nodeObservatoryMetrics.blockchainSyncDelay,
      encryptionOverheadMs: nodeObservatoryMetrics.encryptionOverheadMs,
      metadata: nodeObservatoryMetrics.metadata,
    }).from(nodeObservatoryMetrics);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    if (sortBy === 'timestamp') {
      query.orderBy(sortOrder === 'asc' ? nodeObservatoryMetrics.timestamp : desc(nodeObservatoryMetrics.timestamp));
    } else {
      query.orderBy(desc(nodeObservatoryMetrics.timestamp));
    }

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(nodeObservatoryMetrics);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const metrics = await paginatedQuery;

    return NextResponse.json({
      data: metrics,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
      timeRange: {
        startTime: actualStartTime,
        endTime: actualEndTime,
      },
    });
  } catch (error) {
    console.error('Error fetching observatory metrics:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const body: CreateObservatoryMetricsPayload = await request.json();

    // Validate timestamp
    if (!body.timestamp) {
      return NextResponse.json(
        { error: 'Timestamp is required' },
        { status: 400 }
      );
    }

    // Generate metrics ID
    const metricsId = uuidv4();

    // Create observatory metrics record
    const newMetrics = await db.insert(nodeObservatoryMetrics).values({
      id: metricsId,
      nodeId: nodeId,
      timestamp: body.timestamp,
      networkLatencyMs: body.networkLatencyMs,
      packetLossPercent: body.packetLossPercent,
      jitterMs: body.jitterMs,
      bandwidthMbps: body.bandwidthMbps,
      throughputBps: body.throughputBps,
      dnsResolutionTimeMs: body.dnsResolutionTimeMs,
      tcpConnectionTimeMs: body.tcpConnectionTimeMs,
      httpResponseTimeMs: body.httpResponseTimeMs,
      tcpConnectionFailures: body.tcpConnectionFailures,
      networkErrors: body.networkErrors,
      availabilityScore: body.availabilityScore,
      uptimePercent: body.uptimePercent,
      failedHealthChecks: body.failedHealthChecks,
      successfulHealthChecks: body.successfulHealthChecks,
      dataCenterLatencyMs: body.dataCenterLatencyMs,
      crossRegionLatencyMs: body.crossRegionLatencyMs,
      blockchainSyncDelay: body.blockchainSyncDelay,
      encryptionOverheadMs: body.encryptionOverheadMs,
      metadata: body.metadata || {},
    }).returning();

    return NextResponse.json(newMetrics[0], { status: 201 });
  } catch (error) {
    console.error('Error creating observatory metrics:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Bulk upload endpoint for efficiency
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const metricsList: CreateObservatoryMetricsPayload[] = await request.json();

    if (!Array.isArray(metricsList) || metricsList.length === 0) {
      return NextResponse.json(
        { error: 'Metrics data must be a non-empty array' },
        { status: 400 }
      );
    }

    // Validate each metric
    for (const metric of metricsList) {
      if (!metric.timestamp) {
        return NextResponse.json(
          { error: 'Timestamp is required for each metric' },
          { status: 400 }
        );
      }
    }

    // Prepare bulk insert data
    const bulkData = metricsList.map(metric => ({
      id: uuidv4(),
      nodeId: nodeId,
      timestamp: metric.timestamp,
      networkLatencyMs: metric.networkLatencyMs,
      packetLossPercent: metric.packetLossPercent,
      jitterMs: metric.jitterMs,
      bandwidthMbps: metric.bandwidthMbps,
      throughputBps: metric.throughputBps,
      dnsResolutionTimeMs: metric.dnsResolutionTimeMs,
      tcpConnectionTimeMs: metric.tcpConnectionTimeMs,
      httpResponseTimeMs: metric.httpResponseTimeMs,
      tcpConnectionFailures: metric.tcpConnectionFailures,
      networkErrors: metric.networkErrors,
      availabilityScore: metric.availabilityScore,
      uptimePercent: metric.uptimePercent,
      failedHealthChecks: metric.failedHealthChecks,
      successfulHealthChecks: metric.successfulHealthChecks,
      dataCenterLatencyMs: metric.dataCenterLatencyMs,
      crossRegionLatencyMs: metric.crossRegionLatencyMs,
      blockchainSyncDelay: metric.blockchainSyncDelay,
      encryptionOverheadMs: metric.encryptionOverheadMs,
      metadata: metric.metadata || {},
    }));

    // Bulk insert
    const insertedMetrics = await db.insert(nodeObservatoryMetrics)
      .values(bulkData)
      .returning();

    return NextResponse.json({
      count: insertedMetrics.length,
      metrics: insertedMetrics,
    });
  } catch (error) {
    console.error('Error bulk uploading observatory metrics:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}