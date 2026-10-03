import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodeServiceProofs, nodeEvents } from '@/db/schema';
import { eq, desc, sql, and } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';

interface CreateServiceProofPayload {
  proofType: 'health' | 'capacity' | 'performance' | 'security' | 'compliance' | 'custom';
  proofId: string;
  proofVersion?: string;
  proofData: Record<string, any>;
  verificationMethod?: string;
  validatorId?: string;
  expiresAt?: string;
  metadata?: Record<string, any>;
}

interface UpdateServiceProofPayload {
  status: 'pending' | 'validating' | 'verified' | 'failed' | 'expired';
  validationResult?: Record<string, any>;
  validatorId?: string;
  validatorSignature?: string;
  errorType?: string;
  errorMessage?: string;
  validatedAt?: string;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;
    const { searchParams } = new URL(request.url);

    // Extract query parameters
    const proofType = searchParams.get('proofType');
    const status = searchParams.get('status');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '100'), 1000);
    const offset = (page - 1) * limit;

    // Build query conditions
    const whereConditions = [
      eq(nodeServiceProofs.nodeId, nodeId)
    ];

    if (proofType) {
      whereConditions.push(eq(nodeServiceProofs.proofType, proofType));
    }

    if (status) {
      whereConditions.push(eq(nodeServiceProofs.status, status));
    }

    // Build query
    const query = db.select({
      id: nodeServiceProofs.id,
      nodeId: nodeServiceProofs.nodeId,
      proofType: nodeServiceProofs.proofType,
      status: nodeServiceProofs.status,
      proofId: nodeServiceProofs.proofId,
      proofVersion: nodeServiceProofs.proofVersion,
      createdAt: nodeServiceProofs.createdAt,
      validatedAt: nodeServiceProofs.validatedAt,
      expiresAt: nodeServiceProofs.expiresAt,
      proofData: nodeServiceProofs.proofData,
      validationResult: nodeServiceProofs.validationResult,
      verificationMethod: nodeServiceProofs.verificationMethod,
      validatorId: nodeServiceProofs.validatorId,
      validatorSignature: nodeServiceProofs.validatorSignature,
      errorType: nodeServiceProofs.errorType,
      errorMessage: nodeServiceProofs.errorMessage,
      metadata: nodeServiceProofs.metadata,
    }).from(nodeServiceProofs);

    // Apply filters
    if (whereConditions.length > 0) {
      query.where(and(...whereConditions));
    }

    // Apply sorting
    query.orderBy(desc(nodeServiceProofs.createdAt));

    // Get total count
    const countQuery = db.select({ count: sql`count(*)` }).from(nodeServiceProofs);
    if (whereConditions.length > 0) {
      countQuery.where(and(...whereConditions));
    }
    const [{ count: totalCount }] = await countQuery;

    // Get paginated results
    const paginatedQuery = query.limit(limit).offset(offset);
    const serviceProofs = await paginatedQuery;

    return NextResponse.json({
      data: serviceProofs,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit),
      },
    });
  } catch (error) {
    console.error('Error fetching service proofs:', error);
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
    const body: CreateServiceProofPayload = await request.json();

    // Validate proof type
    if (!['health', 'capacity', 'performance', 'security', 'compliance', 'custom'].includes(body.proofType)) {
      return NextResponse.json(
        { error: 'Invalid proof type. Must be one of: health, capacity, performance, security, compliance, custom' },
        { status: 400 }
      );
    }

    // Check if proof ID already exists
    const existingProof = await db
      .select()
      .from(nodeServiceProofs)
      .where(eq(nodeServiceProofs.proofId, body.proofId))
      .limit(1);
    if (existingProof && existingProof.length > 0) {
      return NextResponse.json(
        { error: 'Proof ID already exists' },
        { status: 409 }
      );
    }

    // Generate service proof ID
    const proofId = uuidv4();

    // Create service proof
    const newProof = await db.insert(nodeServiceProofs).values({
      id: proofId,
      nodeId: nodeId,
      proofType: body.proofType,
      status: 'pending',
      proofId: body.proofId,
      proofVersion: body.proofVersion || '1.0',
      proofData: body.proofData,
      verificationMethod: body.verificationMethod,
      validatorId: body.validatorId,
      expiresAt: body.expiresAt,
      metadata: body.metadata || {},
    }).returning();

    // Log service proof creation event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: 'service_proof_created',
      eventData: {
        proof: newProof[0],
      },
      severity: 'info',
      actorType: 'system',
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(newProof[0], { status: 201 });
  } catch (error) {
    console.error('Error creating service proof:', error);
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
    const proofId = params.id; // In this case, the second ID is the proof ID
    const body: UpdateServiceProofPayload = await request.json();

    // Validate status
    if (!['pending', 'validating', 'verified', 'failed', 'expired'].includes(body.status)) {
      return NextResponse.json(
        { error: 'Invalid status. Must be one of: pending, validating, verified, failed, expired' },
        { status: 400 }
      );
    }

    // Get existing proof
    const existingProof = await db
      .select()
      .from(nodeServiceProofs)
      .where(eq(nodeServiceProofs.id, proofId))
      .limit(1);

    if (!existingProof || existingProof.length === 0) {
      return NextResponse.json(
        { error: 'Service proof not found' },
        { status: 404 }
      );
    }

    // Update service proof
    const updatedProof = await db
      .update(nodeServiceProofs)
      .set({
        status: body.status,
        validationResult: body.validationResult,
        validatorId: body.validatorId,
        validatorSignature: body.validatorSignature,
        errorType: body.errorType,
        errorMessage: body.errorMessage,
        validatedAt: body.validatedAt || new Date().toISOString(),
      })
      .where(eq(nodeServiceProofs.id, proofId))
      .returning();

    // Log service proof verification event
    await db.insert(nodeEvents).values({
      nodeId,
      eventType: body.status === 'verified' ? 'service_proof_verified' :
                 body.status === 'failed' ? 'service_proof_failed' : 'service_proof_updated',
      eventData: {
        proof: updatedProof[0],
      },
      severity: body.status === 'verified' ? 'info' : 'warning',
      actorType: 'validator',
      referenceId: proofId,
      timestamp: new Date().toISOString(),
    });

    return NextResponse.json(updatedProof[0]);
  } catch (error) {
    console.error('Error updating service proof:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}