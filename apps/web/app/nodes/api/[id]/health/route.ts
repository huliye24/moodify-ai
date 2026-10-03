import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodeHealth } from '@/db/schema';
import { eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateHealthPayload {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  apiLatencyMs?: number;
  dbLatencyMs?: number;
  externalServiceLatencyMs?: number;
  servicesAvailable?: boolean;
  criticalServicesHealthy?: boolean;
  errorCount24h?: number;
  warningCount24h?: number;
  cpuThreshold?: number;
  memoryThreshold?: number;
  diskThreshold?: number;
  healthScore?: number;
  details?: Record<string, any>;
  recommendations?: string[];
  maintenanceReason?: string;
  metadata?: Record<string, any>;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;

    // Get current health status
    const currentHealth = await db
      .select()
      .from(nodeHealth)
      .where(eq(nodeHealth.nodeId, nodeId))
      .orderBy(nodeHealth.checkedAt)
      .limit(1);

    if (!currentHealth || currentHealth.length === 0) {
      return NextResponse.json(
        { error: 'No health records found for this node' },
        { status: 404 }
      );
    }

    return NextResponse.json(currentHealth[0]);
  } catch (error) {
    console.error('Error fetching node health:', error);
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
    const body: CreateHealthPayload = await request.json();

    // Validate status
    if (!['healthy', 'degraded', 'unhealthy', 'unknown'].includes(body.status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be one of: healthy, degraded, unhealthy, unknown' },
        { status: 400 }
      );
    }

    // Generate health ID
    const healthId = uuidv4();

    // Create health record
    const newHealth = await db.insert(nodeHealth).values({
      id: healthId,
      nodeId: nodeId,
      status: body.status,
      apiLatencyMs: body.apiLatencyMs,
      dbLatencyMs: body.dbLatencyMs,
      externalServiceLatencyMs: body.externalServiceLatencyMs,
      servicesAvailable: body.servicesAvailable ?? true,
      criticalServicesHealthy: body.criticalServicesHealthy ?? true,
      errorCount24h: body.errorCount24h ?? 0,
      warningCount24h: body.warningCount24h ?? 0,
      cpuThreshold: body.cpuThreshold ?? 90,
      memoryThreshold: body.memoryThreshold ?? 90,
      diskThreshold: body.diskThreshold ?? 90,
      healthScore: body.healthScore ?? 100,
      details: body.details || {},
      recommendations: body.recommendations || [],
      maintenanceReason: body.maintenanceReason,
      metadata: body.metadata || {},
    }).returning();

    // Log health check event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: 'health_check',
      eventData: {
        health: newHealth[0],
      },
      severity: body.status === 'healthy' ? 'info' :
                body.status === 'degraded' ? 'warning' :
                body.status === 'unhealthy' ? 'error' : 'info',
      actorType: 'system',
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(newHealth[0], { status: 201 });
  } catch (error) {
    console.error('Error creating health record:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}