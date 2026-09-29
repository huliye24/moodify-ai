import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodes, nodeCapacityHistory } from '@/db/schema';
import { eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateCapacityHistoryPayload {
  cpuUsagePercent?: number;
  memoryUsagePercent?: number;
  storageUsagePercent?: number;
  networkInMbps?: number;
  networkOutMbps?: number;
  processCount?: number;
  loadAvg1?: string;
  loadAvg5?: string;
  loadAvg15?: string;
  diskReadKBs?: number;
  diskWriteKBs?: number;
  uptimeSeconds?: number;
  temperature?: number;
  metadata?: Record<string, any>;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const { searchParams } = new URL(request.url);

    // Extract query parameters
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '100'), 1000);
    const offset = (page - 1) * limit;
    const startTime = searchParams.get('startTime');
    const endTime = searchParams.get('endTime');
    const sortBy = searchParams.get('sortBy') || 'recordedAt';
    const sortOrder = searchParams.get('sortOrder') || 'desc';

    // Build query conditions
    const whereConditions = [
      eq(nodeCapacityHistory.nodeId, nodeId)
    ];

    if (startTime && endTime) {
      whereConditions.push(
        sql`${nodeCapacityHistory.recordedAt} >= ${startTime} AND ${nodeCapacityHistory.recordedAt} <= ${endTime}`
      );
    }

    // Build query
    const query = db.select({
      id: nodeCapacityHistory.id,
      nodeId: nodeCapacityHistory.nodeId,
      recordedAt: nodeCapacityHistory.recordedAt,
      cpuUsagePercent: nodeCapacityHistory.cpuUsagePercent,
      memoryUsagePercent: nodeCapacityHistory.memoryUsagePercent,
      storageUsagePercent: nodeCapacityHistory.storageUsagePercent,
      networkInMbps: nodeCapacityHistory.networkInMbps,
      networkOutMbps: nodeCapacityHistory.networkOutMbps,
      processCount: nodeCapacityHistory.processCount,
      loadAvg1: nodeCapacityHistory.loadAvg1,
      loadAvg5: nodeCapacityHistory.loadAvg5,
      loadAvg15: nodeCapacityHistory.loadAvg15,
      diskReadKBs: nodeCapacityHistory.diskReadKBs,
      diskWriteKBs: nodeCapacityHistory.diskWriteKBs,
      uptimeSeconds: nodeCapacityHistory.uptimeSeconds,
      temperature: nodeCapacityHistory.temperature,
      metadata: nodeCapacityHistory.metadata,
    }).from(nodeCapacityHistory);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    if (sortBy === 'recordedAt') {
      query.orderBy(sortOrder === 'asc' ? nodeCapacityHistory.recordedAt : desc(nodeCapacityHistory.recordedAt));
    } else {
      query.orderBy(desc(nodeCapacityHistory.recordedAt));
    }

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(nodeCapacityHistory);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const capacityHistory = await paginatedQuery;

    return NextResponse.json({
      data: capacityHistory,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching capacity history:', error);
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
    const body: CreateCapacityHistoryPayload = await request.json();

    // Generate capacity history ID
    const capacityId = uuidv4();

    // Create capacity history record
    const newCapacity = await db.insert(nodeCapacityHistory).values({
      id: capacityId,
      nodeId: nodeId,
      cpuUsagePercent: body.cpuUsagePercent,
      memoryUsagePercent: body.memoryUsagePercent,
      storageUsagePercent: body.storageUsagePercent,
      networkInMbps: body.networkInMbps,
      networkOutMbps: body.networkOutMbps,
      processCount: body.processCount || 0,
      loadAvg1: body.loadAvg1,
      loadAvg5: body.loadAvg5,
      loadAvg15: body.loadAvg15,
      diskReadKBs: body.diskReadKBs,
      diskWriteKBs: body.diskWriteKBs,
      uptimeSeconds: body.uptimeSeconds,
      temperature: body.temperature,
      metadata: body.metadata || {},
    }).returning();

    // Update node's last sync time
    await db.update(nodes)
      .set({
        lastSyncAt: new Date().toISOString(),
      })
      .where(eq(nodes.id, nodeId));

    return NextResponse.json(newCapacity[0], { status: 201 });
  } catch (error) {
    console.error('Error creating capacity history:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}