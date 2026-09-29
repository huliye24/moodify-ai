import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/db/drizzle';
import { nodes, nodeServiceProofs, nodeHealth, nodeCapacityHistory, nodeEvents } from '@/db/schema';
import { eq, desc, sql, and, gte, lt } from 'drizzle-orm';
import { crypto, subtle } from 'crypto';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const nodeId = params.id;

    // 1. Basic node validation
    const nodeInfo = await db
      .select()
      .from(nodes)
      .where(eq(nodes.id, nodeId))
      .limit(1);

    if (!nodeInfo || nodeInfo.length === 0) {
      return NextResponse.json({
        valid: false,
        errors: ['Node not found'],
        validation: {
          nodeExists: false,
          nodeStatus: null,
          nodeRole: null,
        },
      });
    }

    const node = nodeInfo[0];

    // 2. Node status validation
    const statusChecks = {
      isActive: node.status === 'active',
      isDegraded: node.status === 'degraded',
      isOffline: node.status === 'offline',
      isMaintenance: node.status === 'maintenance',
      isRetired: node.status === 'retired',
      isDraft: node.status === 'draft',
    };

    // 3. Service proof validation
    const recentProofs = await db
      .select()
      .from(nodeServiceProofs)
      .where(and(
        eq(nodeServiceProofs.nodeId, nodeId),
        gte(nodeServiceProofs.createdAt, new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
      ))
      .orderBy(desc(nodeServiceProofs.createdAt))
      .limit(5);

    const proofChecks = {
      recentProofs: recentProofs.length,
      lastProofSuccess: recentProofs.length > 0 && recentProofs[0].status === 'verified',
      averageVerificationTime: recentProofs.reduce((sum, proof) => sum + (proof.verificationTimeMs || 0), 0) / recentProofs.length || 0,
      proofFailureRate: recentProofs.filter(proof => proof.status !== 'verified').length / recentProofs.length || 0,
    };

    // 4. Health validation
    const recentHealth = await db
      .select()
      .from(nodeHealth)
      .where(and(
        eq(nodeHealth.nodeId, nodeId),
        gte(nodeHealth.checkedAt, new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString())
      ))
      .orderBy(desc(nodeHealth.checkedAt))
      .limit(1);

    const healthChecks = {
      healthy: recentHealth.length > 0 && recentHealth[0].status === 'healthy',
      degraded: recentHealth.length > 0 && recentHealth[0].status === 'degraded',
      unhealthy: recentHealth.length > 0 && recentHealth[0].status === 'unhealthy',
      healthScore: recentHealth.length > 0 ? recentHealth[0].healthScore : 0,
      lastHealthCheck: recentHealth.length > 0 ? recentHealth[0].checkedAt : null,
    };

    // 5. Capacity validation
    const recentCapacity = await db
      .select()
      .from(nodeCapacityHistory)
      .where(and(
        eq(nodeCapacityHistory.nodeId, nodeId),
        gte(nodeCapacityHistory.recordedAt, new Date(Date.now() - 30 * 60 * 1000).toISOString())
      ))
      .orderBy(desc(nodeCapacityHistory.recordedAt))
      .limit(1);

    const capacityChecks = {
      cpuUsage: recentCapacity.length > 0 ? recentCapacity[0].cpuUsagePercent : 0,
      memoryUsage: recentCapacity.length > 0 ? recentCapacity[0].memoryUsagePercent : 0,
      storageUsage: recentCapacity.length > 0 ? recentCapacity[0].storageUsagePercent : 0,
      networkInMbps: recentCapacity.length > 0 ? recentCapacity[0].networkInMbps : 0,
      networkOutMbps: recentCapacity.length > 0 ? recentCapacity[0].networkOutMbps : 0,
      lastSync: recentCapacity.length > 0 ? recentCapacity[0].recordedAt : null,
    };

    // 6. Heartbeat validation
    const heartbeatChecks = {
      hasHeartbeat: node.lastHeartbeatAt ?
        new Date(node.lastHeartbeatAt).getTime() > Date.now() - 5 * 60 * 1000 :
        false,
      heartbeatAge: node.lastHeartbeatAt ?
        Date.now() - new Date(node.lastHeartbeatAt).getTime() :
        null,
    };

    // 7. Configuration validation
    const configChecks = {
      hasStableId: !!node.stableId,
      hasPublicKey: !!node.publicKey,
      hasIpHash: !!node.ipHash,
      hasHostname: !!node.hostname,
      hasOperatingSystem: !!node.operatingSystem,
      hasRegion: !!node.region,
      hasCountry: !!node.country,
      hasGeoLocation: !!node.latitude && !!node.longitude,
    };

    // 8. Calculate overall validation score
    let validationScore = 100;

    // Deduct points for various failures
    if (!statusChecks.isActive) validationScore -= 20;
    if (!healthChecks.healthy) validationScore -= 20;
    if (!heartbeatChecks.hasHeartbeat) validationScore -= 15;
    if (!configChecks.hasStableId || !configChecks.hasPublicKey) validationScore -= 10;
    if (capacityChecks.cpuUsage > 90) validationScore -= 10;
    if (capacityChecks.memoryUsage > 90) validationScore -= 10;
    if (proofChecks.proofFailureRate > 0.2) validationScore -= 20;

    validationScore = Math.max(0, Math.min(100, validationScore));

    // 9. Determine validation result
    const validationResult = {
      valid: validationScore >= 80,
      score: validationScore,
      status: node.status,
      role: node.role,
      checks: {
        status: statusChecks,
        serviceProof: proofChecks,
        health: healthChecks,
        capacity: capacityChecks,
        heartbeat: heartbeatChecks,
        configuration: configChecks,
      },
      warnings: [],
      errors: [],
    };

    // Add warnings and errors
    if (!statusChecks.isActive) {
      validationResult.errors.push('Node is not in active state');
    }
    if (!healthChecks.healthy) {
      validationResult.warnings.push('Node health is not optimal');
    }
    if (!heartbeatChecks.hasHeartbeat) {
      validationResult.errors.push('Node heartbeat is missing or too old');
    }
    if (!configChecks.hasStableId) {
      validationResult.errors.push('Node missing stable ID');
    }
    if (capacityChecks.cpuUsage > 90) {
      validationResult.warnings.push('CPU usage is high');
    }
    if (capacityChecks.memoryUsage > 90) {
      validationResult.warnings.push('Memory usage is high');
    }
    if (proofChecks.proofFailureRate > 0.2) {
      validationResult.warnings.push('High service proof failure rate');
    }

    return NextResponse.json({
      nodeId,
      validation: validationResult,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error validating node:', error);
    return NextResponse.json(
      {
        valid: false,
        errors: ['Validation failed due to server error'],
        timestamp: new Date().toISOString(),
      },
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
    const { challenge, signature, publicKey } = await request.json();

    // 1. Get node information
    const nodeInfo = await db
      .select()
      .from(nodes)
      .where(eq(nodes.id, nodeId))
      .limit(1);

    if (!nodeInfo || nodeInfo.length === 0) {
      return NextResponse.json({
        valid: false,
        errors: ['Node not found'],
        timestamp: new Date().toISOString(),
      }, { status: 404 });
    }

    const node = nodeInfo[0];

    // 2. Verify the signature
    if (!signature || !challenge) {
      return NextResponse.json({
        valid: false,
        errors: ['Missing signature or challenge'],
        timestamp: new Date().toISOString(),
      }, { status: 400 });
    }

    const publicKeyToUse = publicKey || node.publicKey;
    if (!publicKeyToUse) {
      return NextResponse.json({
        valid: false,
        errors: ['No public key available for verification'],
        timestamp: new Date().toISOString(),
      }, { status: 400 });
    }

    // Verify signature (simplified - in production, use proper crypto library)
    const isValidSignature = await verifySignature(
      publicKeyToUse,
      challenge,
      signature
    );

    if (!isValidSignature) {
      return NextResponse.json({
        valid: false,
        errors: ['Invalid signature'],
        timestamp: new Date().toISOString(),
      }, { status: 401 });
    }

    // 3. Create authentication event
    await db.insert(nodeEvents).values({
      nodeId: nodeId,
      eventType: 'node_authentication',
      eventData: {
        challenge,
        signature,
        publicKey: publicKeyToUse,
        timestamp: new Date().toISOString(),
      },
      severity: 'info',
      actorType: 'node',
      actorId: nodeId,
      timestamp: new Date().toISOString(),
    });

    // 4. Update last heartbeat if provided
    if (challenge.includes('heartbeat')) {
      await db.update(nodes)
        .set({
          lastHeartbeatAt: new Date().toISOString(),
        })
        .where(eq(nodes.id, nodeId));
    }

    return NextResponse.json({
      valid: true,
      message: 'Node authentication successful',
      nodeId,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error validating node:', error);
    return NextResponse.json(
      {
        valid: false,
        errors: ['Validation failed due to server error'],
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

// Helper function to verify signature
async function verifySignature(publicKey: string, message: string, signature: string): Promise<boolean> {
  try {
    // This is a simplified signature verification
    // In a production environment, you would use proper crypto libraries
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    const signatureBuffer = Buffer.from(signature, 'base64');

    // Convert public key to appropriate format
    const publicKeyBuffer = Buffer.from(publicKey.replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', ''), 'base64');

    // Verify signature (this is a simplified example)
    // In production, use proper crypto operations
    const isValid = await subtle.verify(
      { name: 'RSA-PSS' },
      await subtle.importKey(
        'spki',
        publicKeyBuffer,
        { name: 'RSA-PSS' },
        false,
        ['verify']
      ),
      signatureBuffer,
      data
    );

    return isValid;
  } catch (error) {
    console.error('Signature verification error:', error);
    return false;
  }
}