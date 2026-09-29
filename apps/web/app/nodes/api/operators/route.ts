import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { operators } from '@/db/schema';
import { ilike, or, eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateOperatorPayload {
  type: 'resident' | 'organization';
  residentId?: string;
  organizationId?: string;
  organizationName?: string;
  contactEmail?: string;
  contactPhone?: string;
  responsibleParty?: string;
  role?: string;
  status?: 'active' | 'inactive' | 'suspended' | 'pending';
  apiKeys?: string[];
  permissions?: string[];
  termsAcceptedAt?: string;
  metadata?: Record<string, any>;
}

interface UpdateOperatorPayload extends Partial<CreateOperatorPayload> {
  status?: 'active' | 'inactive' | 'suspended' | 'pending';
  lastLoginAt?: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Extract query parameters
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100);
    const offset = (page - 1) * limit;
    const type = searchParams.get('type');
    const status = searchParams.get('status');
    const search = searchParams.get('search');
    const sortBy = searchParams.get('sortBy') || 'createdAt';
    const sortOrder = searchParams.get('sortOrder') || 'desc';

    // Build query conditions
    const whereConditions = [];

    if (type) {
      whereConditions.push(eq(operators.type, type));
    }

    if (status) {
      whereConditions.push(eq(operators.status, status));
    }

    if (search) {
      whereConditions.push(
        or(
          ilike(operators.residentId, `%${search}%`),
          ilike(operators.organizationName, `%${search}%`),
          ilike(operators.contactEmail, `%${search}%`),
          ilike(operators.contactPhone, `%${search}%`),
          ilike(operators.responsibleParty, `%${search}%`)
        )
      );
    }

    // Build query
    const query = db.select({
      id: operators.id,
      type: operators.type,
      residentId: operators.residentId,
      organizationId: operators.organizationId,
      organizationName: operators.organizationName,
      contactEmail: operators.contactEmail,
      contactPhone: operators.contactPhone,
      responsibleParty: operators.responsibleParty,
      role: operators.role,
      status: operators.status,
      apiKeys: operators.apiKeys,
      permissions: operators.permissions,
      createdAt: operators.createdAt,
      updatedAt: operators.updatedAt,
      lastLoginAt: operators.lastLoginAt,
      termsAcceptedAt: operators.termsAcceptedAt,
      lastComplianceReviewAt: operators.lastComplianceReviewAt,
      metadata: operators.metadata,
    }).from(operators);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    if (sortBy === 'createdAt') {
      query.orderBy(sortOrder === 'asc' ? operators.createdAt : desc(operators.createdAt));
    } else if (sortBy === 'name' && type === 'organization') {
      query.orderBy(sortOrder === 'asc' ? operators.organizationName : desc(operators.organizationName));
    } else if (sortBy === 'status') {
      query.orderBy(sortOrder === 'asc' ? operators.status : desc(operators.status));
    } else {
      query.orderBy(desc(operators.createdAt));
    }

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(operators);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const operatorsList = await paginatedQuery;

    return NextResponse.json({
      data: operatorsList,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching operators:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: CreateOperatorPayload = await request.json();

    // Validate required fields based on type
    if (body.type === 'resident' && !body.residentId) {
      return NextResponse.json(
        { error: 'Resident ID is required for resident operators' },
        { status: 400 }
      );
    }

    if (body.type === 'organization' && (!body.organizationId || !body.organizationName)) {
      return NextResponse.json(
        { error: 'Organization ID and name are required for organization operators' },
        { status: 400 }
      );
    }

    // Validate status
    if (body.status && !['active', 'inactive', 'suspended', 'pending'].includes(body.status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be one of: active, inactive, suspended, pending' },
        { status: 400 }
      );
    }

    // Generate operator ID
    const operatorId = uuidv4();

    // Create operator
    const newOperator = await db.insert(operators).values({
      id: operatorId,
      type: body.type,
      residentId: body.residentId,
      organizationId: body.organizationId,
      organizationName: body.organizationName,
      contactEmail: body.contactEmail,
      contactPhone: body.contactPhone,
      responsibleParty: body.responsibleParty,
      role: body.role,
      status: body.status || 'active',
      apiKeys: body.apiKeys || [],
      permissions: body.permissions || [],
      termsAcceptedAt: body.termsAcceptedAt,
      metadata: body.metadata || {},
    }).returning();

    return NextResponse.json(newOperator[0], { status: 201 });
  } catch (error) {
    console.error('Error creating operator:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body: UpdateOperatorPayload = await request.json();
    const operatorId = body.id;

    if (!operatorId) {
      return NextResponse.json(
        { error: 'Operator ID is required' },
        { status: 400 }
      );
    }

    // Check if operator exists
    const existingOperator = await db
      .select()
      .from(operators)
      .where(eq(operators.id, operatorId))
      .limit(1);

    if (!existingOperator || existingOperator.length === 0) {
      return NextResponse.json(
        { error: 'Operator not found' },
        { status: 404 }
      );
    }

    // Validate status if provided
    if (body.status && !['active', 'inactive', 'suspended', 'pending'].includes(body.status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be one of: active, inactive, suspended, pending' },
        { status: 400 }
      );
    }

    // Update operator
    const updatedOperator = await db
      .update(operators)
      .set({
        ...body,
        updatedAt: new Date().toISOString(),
        lastLoginAt: body.lastLoginAt,
      })
      .where(eq(operators.id, operatorId))
      .returning();

    return NextResponse.json(updatedOperator[0]);
  } catch (error) {
    console.error('Error updating operator:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}