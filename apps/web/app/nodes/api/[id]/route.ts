import { NextRequest, NextResponse } from 'next/server';
import { eq } from 'drizzle-orm';
import { db } from '@/db/drizzle';
import { nodes, nodeCapacityHistory, nodeHealth, nodeServiceProofs, nodeEvents, operators } from '@/db/schema';
import type { Node } from '@/db/schema';

interface NodeResponse extends Node {
  capacityHistory?: any[];
  health?: any;
  serviceProofs?: any[];
  events?: any[];
  operator?: any;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;

    // Get node details
    const node = await db.select().from(nodes).where(eq(nodes.id, nodeId));

    if (!node || node.length === 0) {
      return NextResponse.json(
        { error: 'Node not found' },
        { status: 404 }
      );
    }

    const nodeData = node[0];

    // Get node capacity history (last 100 entries)
    const capacityHistory = await db
      .select()
      .from(nodeCapacityHistory)
      .where(eq(nodeCapacityHistory.nodeId, nodeId))
      .orderBy(nodeCapacityHistory.recordedAt)
      .limit(100);

    // Get current node health
    const health = await db
      .select()
      .from(nodeHealth)
      .where(eq(nodeHealth.nodeId, nodeId))
      .orderBy(nodeHealth.checkedAt)
      .limit(1);

    // Get node service proofs
    const serviceProofs = await db
      .select()
      .from(nodeServiceProofs)
      .where(eq(nodeServiceProofs.nodeId, nodeId))
      .orderBy(nodeServiceProofs.createdAt);

    // Get node events (last 50 events)
    const events = await db
      .select()
      .from(nodeEvents)
      .where(eq(nodeEvents.nodeId, nodeId))
      .orderBy(nodeEvents.timestamp)
      .limit(50);

    // Get operator information
    let operator = null;
    if (nodeData.operatorResidentId) {
      operator = await db
        .select()
        .from(operators)
        .where(eq(operators.residentId, nodeData.operatorResidentId))
        .limit(1);
    } else if (nodeData.operatorOrganizationId) {
      operator = await db
        .select()
        .from(operators)
        .where(eq(operators.organizationId, nodeData.operatorOrganizationId))
        .limit(1);
    }

    const response: NodeResponse = {
      ...nodeData,
      capacityHistory: capacityHistory,
      health: health[0] || null,
      serviceProofs: serviceProofs,
      events: events,
      operator: operator[0] || null,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching node:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const body = await request.json();
    const {
      name,
      description,
      role,
      status,
      cloudProvider,
      region,
      availabilityZone,
      instanceType,
      hostname,
      operatingSystem,
      kernelVersion,
      cpuCores,
      cpuModel,
      memoryGB,
      storageGB,
      bandwidthMbps,
      hasGPU,
      gpuCount,
      gpuModel,
      gpuMemoryGB,
      country,
      city,
      latitude,
      longitude,
      operatorType,
      operatorResidentId,
      operatorOrganizationId,
      tags,
      metadata
    } = body;

    // Verify node exists
    const existingNode = await db.select().from(nodes).where(eq(nodes.id, nodeId));
    if (!existingNode || existingNode.length === 0) {
      return NextResponse.json(
        { error: 'Node not found' },
        { status: 404 }
      );
    }

    // Check if operator exists if provided
    if (operatorType === 'resident' && operatorResidentId) {
      const operator = await db
        .select()
        .from(operators)
        .where(eq(operators.residentId, operatorResidentId))
        .limit(1);
      if (!operator || operator.length === 0) {
        return NextResponse.json(
          { error: 'Resident operator not found' },
          { status: 400 }
        );
      }
    } else if (operatorType === 'organization' && operatorOrganizationId) {
      const operator = await db
        .select()
        .from(operators)
        .where(eq(operators.organizationId, operatorOrganizationId))
        .limit(1);
      if (!operator || operator.length === 0) {
        return NextResponse.json(
          { error: 'Organization operator not found' },
          { status: 400 }
        );
      }
    }

    // Update node
    const updateData: any = {
      name,
      description,
      role,
      status,
      cloudProvider,
      region,
      availabilityZone,
      instanceType,
      hostname,
      operatingSystem,
      kernelVersion,
      cpuCores,
      cpuModel,
      memoryGB,
      storageGB,
      bandwidthMbps,
      hasGPU,
      gpuCount,
      gpuModel,
      gpuMemoryGB,
      country,
      city,
      latitude,
      longitude,
      operatorType,
      operatorResidentId,
      operatorOrganizationId,
      tags,
      metadata,
    };

    // Only include fields that are provided
    Object.keys(updateData).forEach(key => {
      if (updateData[key] === undefined) {
        delete updateData[key];
      }
    });

    const updatedNode = await db
      .update(nodes)
      .set({
        ...updateData,
        updatedAt: new Date().toISOString(),
      })
      .where(eq(nodes.id, nodeId))
      .returning();

    // Log node update event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: 'node_updated',
      eventData: {
        changes: updateData,
      },
      severity: 'info',
      actorType: 'admin',
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(updatedNode[0]);
  } catch (error) {
    console.error('Error updating node:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;

    // Verify node exists
    const existingNode = await db.select().from(nodes).where(eq(nodes.id, nodeId));
    if (!existingNode || existingNode.length === 0) {
      return NextResponse.json(
        { error: 'Node not found' },
        { status: 404 }
      );
    }

    // Delete node (cascade will handle related records)
    await db.delete(nodes).where(eq(nodes.id, nodeId));

    // Log node deletion event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: 'node_deleted',
      eventData: {},
      severity: 'warning',
      actorType: 'admin',
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json({ message: 'Node deleted successfully' });
  } catch (error) {
    console.error('Error deleting node:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}