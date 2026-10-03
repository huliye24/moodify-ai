import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodeEvents } from '@/db/schema';
import { eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateEventPayload {
  eventType: string;
  eventData?: Record<string, any>;
  severity?: 'info' | 'warning' | 'error' | 'critical';
  actorType?: 'system' | 'operator' | 'admin' | 'user';
  actorId?: string;
  correlationId?: string;
  referenceId?: string;
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
    const eventType = searchParams.get('eventType');
    const severity = searchParams.get('severity');
    const startTime = searchParams.get('startTime');
    const endTime = searchParams.get('endTime');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '100'), 1000);
    const offset = (page - 1) * limit;
    const sortBy = searchParams.get('sortBy') || 'timestamp';
    const sortOrder = searchParams.get('sortOrder') || 'desc';

    // Build query conditions
    const whereConditions = [
      eq(nodeEvents.nodeId, nodeId)
    ];

    if (eventType) {
      whereConditions.push(eq(nodeEvents.eventType, eventType));
    }

    if (severity) {
      whereConditions.push(eq(nodeEvents.severity, severity));
    }

    if (startTime && endTime) {
      whereConditions.push(
        sql`${nodeEvents.timestamp} >= ${startTime} AND ${nodeEvents.timestamp} <= ${endTime}`
      );
    }

    // Build query
    const query = db.select({
      id: nodeEvents.id,
      nodeId: nodeEvents.nodeId,
      eventType: nodeEvents.eventType,
      eventData: nodeEvents.eventData,
      timestamp: nodeEvents.timestamp,
      severity: nodeEvents.severity,
      actorType: nodeEvents.actorType,
      actorId: nodeEvents.actorId,
      correlationId: nodeEvents.correlationId,
      referenceId: nodeEvents.referenceId,
      metadata: nodeEvents.metadata,
    }).from(nodeEvents);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    if (sortBy === 'timestamp') {
      query.orderBy(sortOrder === 'asc' ? nodeEvents.timestamp : desc(nodeEvents.timestamp));
    } else {
      query.orderBy(desc(nodeEvents.timestamp));
    }

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(nodeEvents);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const events = await paginatedQuery;

    return NextResponse.json({
      data: events,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching node events:', error);
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
    const body: CreateEventPayload = await request.json();

    // Validate event type
    const validEventTypes = [
      'node_created', 'node_updated', 'node_deleted',
      'status_changed', 'heartbeat_received', 'heartbeat_missed',
      'capacity_updated', 'health_check', 'service_proof_created',
      'service_proof_verified', 'service_proof_failed', 'maintenance_started',
      'maintenance_ended', 'alert_triggered', 'alert_resolved'
    ];

    if (!validEventTypes.includes(body.eventType)) {
      return NextResponse.json(
        { error: 'Invalid event type' },
        { status: 400 }
      );
    }

    // Validate severity
    if (body.severity && !['info', 'warning', 'error', 'critical'].includes(body.severity)) {
      return NextResponse.json(
        { error: 'Invalid severity. Must be one of: info, warning, error, critical' },
        { status: 400 }
      );
    }

    // Validate actor type
    if (body.actorType && !['system', 'operator', 'admin', 'user'].includes(body.actorType)) {
      return NextResponse.json(
        { error: 'Invalid actor type. Must be one of: system, operator, admin, user' },
        { status: 400 }
      );
    }

    // Generate event ID
    const eventId = uuidv4();

    // Create event
    const newEvent = await db.insert(nodeEvents).values({
      id: eventId,
      nodeId: nodeId,
      eventType: body.eventType,
      eventData: body.eventData || {},
      timestamp: new Date().toISOString(),
      severity: body.severity || 'info',
      actorType: body.actorType || 'system',
      actorId: body.actorId,
      correlationId: body.correlationId,
      referenceId: body.referenceId,
      metadata: body.metadata || {},
    }).returning();

    return NextResponse.json(newEvent[0], { status: 201 });
  } catch (error) {
    console.error('Error creating event:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}