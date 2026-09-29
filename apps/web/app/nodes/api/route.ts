import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodes, nodeCapacityHistory, nodeHealth, nodeServiceProofs, nodeEvents, operators } from '@/db/schema';
import { ilike, or, eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateNodePayload {
  name: string;
  description?: string;
  role: 'compute' | 'ai' | 'storage' | 'verification';
  status?: 'draft' | 'active' | 'degraded' | 'offline' | 'maintenance' | 'retired';
  stableId: string;
  nodeIdAlias?: string;
  publicKey?: string;
  ipHash?: string;
  cloudProvider?: string;
  region?: string;
  availabilityZone?: string;
  instanceType?: string;
  hostname?: string;
  operatingSystem?: string;
  kernelVersion?: string;
  cpuCores?: number;
  cpuModel?: string;
  memoryGB?: number;
  storageGB?: number;
  bandwidthMbps?: number;
  hasGPU?: boolean;
  gpuCount?: number;
  gpuModel?: string;
  gpuMemoryGB?: number;
  country?: string;
  city?: string;
  latitude?: string;
  longitude?: string;
  operatorType?: 'resident' | 'organization';
  operatorResidentId?: string;
  operatorOrganizationId?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// Helper function to generate a slug from name
function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .trim();
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Extract query parameters
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100);
    const offset = (page - 1) * limit;

    const role = searchParams.get('role');
    const status = searchParams.get('status');
    const cloudProvider = searchParams.get('cloudProvider');
    const operatorId = searchParams.get('operatorId');
    const search = searchParams.get('search');
    const sortBy = searchParams.get('sortBy') || 'createdAt';
    const sortOrder = searchParams.get('sortOrder') || 'desc';

    // Build query conditions
    const whereConditions = [];

    if (role) {
      whereConditions.push(eq(nodes.role, role));
    }

    if (status) {
      whereConditions.push(eq(nodes.status, status));
    }

    if (cloudProvider) {
      whereConditions.push(eq(nodes.cloudProvider, cloudProvider));
    }

    if (operatorId) {
      whereConditions.push(
        or(
          eq(nodes.operatorResidentId, operatorId),
          eq(nodes.operatorOrganizationId, operatorId)
        )
      );
    }

    if (search) {
      whereConditions.push(
        or(
          ilike(nodes.name, `%${search}%`),
          ilike(nodes.description, `%${search}%`),
          ilike(nodes.hostname, `%${search}%`),
          ilike(nodes.nodeIdAlias, `%${search}%`)
        )
      );
    }

    // Build query
    const query = db.select({
      id: nodes.id,
      slug: nodes.slug,
      name: nodes.name,
      description: nodes.description,
      role: nodes.role,
      status: nodes.status,
      cloudProvider: nodes.cloudProvider,
      region: nodes.region,
      availabilityZone: nodes.availabilityZone,
      hostname: nodes.hostname,
      operatingSystem: nodes.operatingSystem,
      cpuCores: nodes.cpuCores,
      memoryGB: nodes.memoryGB,
      storageGB: nodes.storageGB,
      bandwidthMbps: nodes.bandwidthMbps,
      hasGPU: nodes.hasGPU,
      gpuCount: nodes.gpuCount,
      gpuModel: nodes.gpuModel,
      gpuMemoryGB: nodes.gpuMemoryGB,
      country: nodes.country,
      city: nodes.city,
      latitude: nodes.latitude,
      longitude: nodes.longitude,
      operatorType: nodes.operatorType,
      operatorResidentId: nodes.operatorResidentId,
      operatorOrganizationId: nodes.operatorOrganizationId,
      createdAt: nodes.createdAt,
      updatedAt: nodes.updatedAt,
      lastHeartbeatAt: nodes.lastHeartbeatAt,
      tags: nodes.tags,
      metadata: nodes.metadata,
    }).from(nodes);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    if (sortBy === 'createdAt') {
      query.orderBy(sortOrder === 'asc' ? nodes.createdAt : desc(nodes.createdAt));
    } else if (sortBy === 'name') {
      query.orderBy(sortOrder === 'asc' ? nodes.name : desc(nodes.name));
    } else if (sortBy === 'status') {
      query.orderBy(sortOrder === 'asc' ? nodes.status : desc(nodes.status));
    } else if (sortBy === 'role') {
      query.orderBy(sortOrder === 'asc' ? nodes.role : desc(nodes.role));
    } else {
      query.orderBy(desc(nodes.createdAt));
    }

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(nodes);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const nodesList = await paginatedQuery;

    // Get operator information for each node
    const nodesWithOperators = await Promise.all(
      nodesList.map(async (node) => {
        let operator = null;
        if (node.operatorResidentId) {
          const [resOp] = await db
            .select()
            .from(operators)
            .where(eq(operators.residentId, node.operatorResidentId))
            .limit(1);
          operator = resOp;
        } else if (node.operatorOrganizationId) {
          const [orgOp] = await db
            .select()
            .from(operators)
            .where(eq(operators.organizationId, node.operatorOrganizationId))
            .limit(1);
          operator = orgOp;
        }

        return {
          ...node,
          operator,
        };
      })
    );

    return NextResponse.json({
      data: nodesWithOperators,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching nodes:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: CreateNodePayload = await request.json();

    // Validate required fields
    if (!body.name || !body.role || !body.stableId) {
      return NextResponse.json(
        { error: 'Missing required fields: name, role, stableId' },
        { status: 400 }
      );
    }

    // Validate role and status
    if (!['compute', 'ai', 'storage', 'verification'].includes(body.role)) {
      return NextResponse.json(
        { error: 'Invalid role. Must be one of: compute, ai, storage, verification' },
        { status: 400 }
      );
    }

    if (body.status && !['draft', 'active', 'degraded', 'offline', 'maintenance', 'retired'].includes(body.status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be one of: draft, active, degraded, offline, maintenance, retired' },
        { status: 400 }
      );
    }

    // Check if operator exists if provided
    if (body.operatorType === 'resident' && body.operatorResidentId) {
      const operator = await db
        .select()
        .from(operators)
        .where(eq(operators.residentId, body.operatorResidentId))
        .limit(1);
      if (!operator || operator.length === 0) {
        return NextResponse.json(
          { error: 'Resident operator not found' },
          { status: 400 }
        );
      }
    } else if (body.operatorType === 'organization' && body.operatorOrganizationId) {
      const operator = await db
        .select()
        .from(operators)
        .where(eq(operators.organizationId, body.operatorOrganizationId))
        .limit(1);
      if (!operator || operator.length === 0) {
        return NextResponse.json(
          { error: 'Organization operator not found' },
          { status: 400 }
        );
      }
    }

    // Generate node ID and slug
    const nodeId = uuidv4();
    const slug = generateSlug(body.name);

    // Check if slug already exists
    const existingSlug = await db
      .select()
      .from(nodes)
      .where(eq(nodes.slug, slug))
      .limit(1);
    if (existingSlug && existingSlug.length > 0) {
      return NextResponse.json(
        { error: 'Node with this name already exists' },
        { status: 409 }
      );
    }

    // Create node
    const newNode = await db.insert(nodes).values({
      id: nodeId,
      slug,
      name: body.name,
      description: body.description || '',
      role: body.role,
      status: body.status || 'draft',
      stableId: body.stableId,
      nodeIdAlias: body.nodeIdAlias,
      publicKey: body.publicKey,
      ipHash: body.ipHash,
      cloudProvider: body.cloudProvider,
      region: body.region,
      availabilityZone: body.availabilityZone,
      instanceType: body.instanceType,
      hostname: body.hostname,
      operatingSystem: body.operatingSystem,
      kernelVersion: body.kernelVersion,
      cpuCores: body.cpuCores,
      cpuModel: body.cpuModel,
      memoryGB: body.memoryGB,
      storageGB: body.storageGB,
      bandwidthMbps: body.bandwidthMbps,
      hasGPU: body.hasGPU || false,
      gpuCount: body.gpuCount || 0,
      gpuModel: body.gpuModel,
      gpuMemoryGB: body.gpuMemoryGB || 0,
      country: body.country,
      city: body.city,
      latitude: body.latitude,
      longitude: body.longitude,
      operatorType: body.operatorType,
      operatorResidentId: body.operatorResidentId,
      operatorOrganizationId: body.operatorOrganizationId,
      tags: body.tags || [],
      metadata: body.metadata || {},
    }).returning();

    // Log node creation event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: 'node_created',
      eventData: {
        node: newNode[0],
      },
      severity: 'info',
      actorType: 'admin',
      timestamp: new Date().toISOString(),
    });

    // Get the created node with related data
    const createdNode = await db
      .select({
        id: nodes.id,
        slug: nodes.slug,
        name: nodes.name,
        description: nodes.description,
        role: nodes.role,
        status: nodes.status,
        cloudProvider: nodes.cloudProvider,
        region: nodes.region,
        availabilityZone: nodes.availabilityZone,
        hostname: nodes.hostname,
        operatingSystem: nodes.operatingSystem,
        cpuCores: nodes.cpuCores,
        memoryGB: nodes.memoryGB,
        storageGB: nodes.storageGB,
        bandwidthMbps: nodes.bandwidthMbps,
        hasGPU: nodes.hasGPU,
        gpuCount: nodes.gpuCount,
        gpuModel: nodes.gpuModel,
        gpuMemoryGB: nodes.gpuMemoryGB,
        country: nodes.country,
        city: nodes.city,
        latitude: nodes.latitude,
        longitude: nodes.longitude,
        operatorType: nodes.operatorType,
        operatorResidentId: nodes.operatorResidentId,
        operatorOrganizationId: nodes.operatorOrganizationId,
        createdAt: nodes.createdAt,
        updatedAt: nodes.updatedAt,
        lastHeartbeatAt: nodes.lastHeartbeatAt,
        tags: nodes.tags,
        metadata: nodes.metadata,
      })
      .from(nodes)
      .where(eq(nodes.id, nodeId))
      .limit(1);

    // Get operator information
    let operator = null;
    if (newNode[0].operatorResidentId) {
      operator = await db
        .select()
        .from(operators)
        .where(eq(operators.residentId, newNode[0].operatorResidentId))
        .limit(1);
    } else if (newNode[0].operatorOrganizationId) {
      operator = await db
        .select()
        .from(operators)
        .where(eq(operators.organizationId, newNode[0].operatorOrganizationId))
        .limit(1);
    }

    const response = {
      ...createdNode[0],
      operator: operator[0] || null,
    };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    console.error('Error creating node:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}