/**
 * MOOD Protocol API - Domain Service Adapters
 *
 * Thin adapters that expose domain authority from MPF-001 through MPF-004.
 * These do NOT contain business logic - they only delegate.
 *
 * The API route handlers MUST use these services instead of
 * accessing storage directly.
 */

import crypto from 'crypto';

// ==================== MPF-001 Mainnet Facts ====================

/**
 * Mainnet Facts Service - delegates to MPF-001
 */
export class MainnetService {
  constructor(adapter = null) {
    this.adapter = adapter;
  }

  /**
   * Get mainnet facts
   * @returns {Promise<object|null>} Mainnet facts from MPF-001
   */
  async getMainnetFacts() {
    try {
      // Read from MPF-001 canonical source
      const fs = await import('fs');
      const path = await import('path');

      const lockPath = path.join(process.cwd(), 'protocol', 'mainnet.lock.json');

      if (fs.existsSync(lockPath)) {
        const data = fs.readFileSync(lockPath, 'utf8');
        return JSON.parse(data);
      }

      // Fall back to mainnet.json
      const mainnetPath = path.join(process.cwd(), 'protocol', 'mainnet.json');
      if (fs.existsSync(mainnetPath)) {
        const data = fs.readFileSync(mainnetPath, 'utf8');
        return JSON.parse(data);
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Get protocol status
   * @returns {Promise<object>} Protocol status
   */
  async getProtocolStatus() {
    const facts = await this.getMainnetFacts();
    return {
      status: facts ? (facts.status || 'active') : 'unknown',
      network: facts?.network || 'mainnet',
      schemaVersion: facts?.schemaVersion || '1.0.0'
    };
  }
}

// ==================== MPF-002 Contributions ====================

/**
 * Contribution Service - delegates to MPF-002 authority
 */
export class ContributionService {
  constructor(adapter = null) {
    this.adapter = adapter;
    this.contributions = [];
  }

  /**
   * Load contributions from fixture or adapter
   */
  async loadContributions() {
    // In production this would call MPF-002 module
    // For API testing, use fixtures or in-memory data
    return this.contributions;
  }

  /**
   * List contributions with filters
   * @param {object} filters - Filter options
   * @returns {Promise<Array>} Filtered contributions
   */
  async listContributions(filters = {}) {
    const all = await this.loadContributions();
    let results = [...all];

    if (filters.contributor) {
      results = results.filter(c =>
        c.contributor?.id === filters.contributor ||
        c.contributorId === filters.contributor
      );
    }

    if (filters.category) {
      results = results.filter(c => c.category === filters.category);
    }

    if (filters.status) {
      results = results.filter(c => c.status === filters.status);
    }

    return results;
  }

  /**
   * Get contribution by ID
   * @param {string} contributionId - Contribution ID
   * @returns {Promise<object|null>} Contribution or null
   */
  async getContribution(contributionId) {
    const all = await this.loadContributions();
    return all.find(c => c.id === contributionId || c.contributionId === contributionId) || null;
  }

  /**
   * Sanitize contribution for public API
   * @param {object} contribution - Raw contribution
   * @returns {object} Public-safe contribution
   */
  sanitizeForPublic(contribution) {
    return {
      contributionId: contribution.id || contribution.contributionId,
      contributor: {
        type: contribution.contributor?.type || 'wallet',
        id: contribution.contributor?.id || contribution.contributorId
      },
      category: contribution.category,
      title: contribution.title,
      description: contribution.description,
      submittedAt: contribution.submittedAt,
      status: contribution.status,
      scores: contribution.scores,
      policyVersion: contribution.policyVersion
      // Excludes: private evidence, internal metadata
    };
  }
}

// ==================== MPF-003 Reputation ====================

/**
 * Reputation Service - delegates to MPF-003 authority
 */
export class ReputationService {
  constructor(adapter = null) {
    this.adapter = adapter;
    this.profiles = new Map();
    this.snapshots = new Map();
  }

  /**
   * Get contributor profile
   * @param {string} protocolId - Contributor protocol ID
   * @returns {Promise<object|null>} Profile or null
   */
  async getProfile(protocolId) {
    return this.profiles.get(protocolId) || null;
  }

  /**
   * Get reputation snapshot
   * @param {string} protocolId - Contributor protocol ID
   * @returns {Promise<object|null>} Latest snapshot or null
   */
  async getLatestSnapshot(protocolId) {
    const snapshots = this.snapshots.get(protocolId) || [];
    if (snapshots.length === 0) return null;

    return snapshots.sort((a, b) =>
      new Date(b.generatedAt) - new Date(a.generatedAt)
    )[0];
  }

  /**
   * Get all snapshots for contributor
   * @param {string} protocolId - Contributor protocol ID
   * @returns {Promise<Array>} All snapshots
   */
  async getAllSnapshots(protocolId) {
    return this.snapshots.get(protocolId) || [];
  }

  /**
   * Sanitize snapshot for public API
   * Preserves aggregate = null per MPF-003 spec
   * @param {object} snapshot - Raw snapshot
   * @returns {object} Public-safe snapshot
   */
  sanitizeForPublic(snapshot) {
    return {
      snapshotId: snapshot.snapshotId,
      snapshotVersion: snapshot.snapshotVersion,
      protocolId: snapshot.protocolId,
      epochId: snapshot.epochId,
      policyVersion: snapshot.policyVersion,
      epochPolicyVersion: snapshot.epochPolicyVersion,
      dimensions: snapshot.dimensions,
      aggregate: snapshot.aggregate,  // null is preserved
      verifiedContributionCount: snapshot.verifiedContributionCount,
      categoryDiversity: snapshot.categoryDiversity,
      confidence: snapshot.confidence,
      generatedAt: snapshot.generatedAt,
      snapshotFingerprint: snapshot.snapshotFingerprint
    };
  }
}

// ==================== MPF-004 Nodes ====================

/**
 * Node Registry Service - delegates to MPF-004 authority
 */
export class NodeService {
  constructor(adapter = null) {
    this.adapter = adapter;
    this.nodes = new Map();
  }

  /**
   * Load all nodes
   * @returns {Promise<Array>} All nodes
   */
  async loadNodes() {
    return Array.from(this.nodes.values());
  }

  /**
   * List nodes with filters
   * @param {object} filters - Filter options
   * @returns {Promise<Array>} Filtered nodes
   */
  async listNodes(filters = {}) {
    let nodes = await this.loadNodes();

    if (filters.nodeType) {
      nodes = nodes.filter(n => n.nodeType === filters.nodeType);
    }

    if (filters.lifecycleStatus) {
      nodes = nodes.filter(n => n.lifecycleStatus === filters.lifecycleStatus);
    }

    if (filters.country) {
      nodes = nodes.filter(n => n.region?.countryCode === filters.country);
    }

    if (filters.health) {
      nodes = nodes.filter(n => n.health?.status === filters.health);
    }

    return nodes;
  }

  /**
   * Get node by ID
   * @param {string} nodeId - Node ID
   * @returns {Promise<object|null>} Node or null
   */
  async getNode(nodeId) {
    return this.nodes.get(nodeId) || null;
  }

  /**
   * Get node capabilities (separating declared vs verified)
   * @param {string} nodeId - Node ID
   * @returns {Promise<object|null>} Capability manifest or null
   */
  async getCapabilities(nodeId) {
    const node = await this.getNode(nodeId);
    return node?.capabilityManifest || null;
  }

  /**
   * Get node health
   * @param {string} nodeId - Node ID
   * @returns {Promise<object|null>} Health info or null
   */
  async getHealth(nodeId) {
    const node = await this.getNode(nodeId);
    if (!node) return null;

    return {
      nodeId,
      currentStatus: node.health?.status || 'unknown',
      lastObservedAt: node.health?.observedAt
    };
  }

  /**
   * Sanitize node for public API
   * @param {object} node - Raw node
   * @returns {object} Public-safe node
   */
  sanitizeForPublic(node) {
    return {
      nodeId: node.nodeId,
      nodeType: node.nodeType,
      displayName: node.displayName,
      region: {
        countryCode: node.region?.countryCode,
        precision: node.region?.precision
        // City/region details omitted for privacy
      },
      lifecycleStatus: node.lifecycleStatus,
      health: {
        status: node.health?.status || 'unknown',
        observedAt: node.health?.observedAt
      },
      verification: {
        status: node.verification?.status || 'pending'
      },
      registeredAt: node.registeredAt
      // Excludes: endpoint URI unless active, private fields
    };
  }
}

// ==================== API Aggregator ====================

/**
 * Aggregate API service that coordinates all domain services
 */
export class ProtocolApiService {
  constructor() {
    this.mainnet = new MainnetService();
    this.contributions = new ContributionService();
    this.reputation = new ReputationService();
    this.nodes = new NodeService();
  }

  /**
   * Build network summary from authoritative sources
   * @returns {Promise<object>} Network summary
   */
  async buildNetworkSummary() {
    const [mainnet, contributions, profiles, nodes] = await Promise.all([
      this.mainnet.getProtocolStatus(),
      this.contributions.loadContributions(),
      Promise.resolve(Array.from(this.reputation.profiles.keys())),
      this.nodes.loadNodes()
    ]);

    const verifiedContributions = contributions.filter(c =>
      c.status === 'verified' || c.status === 'finalized' || c.status === 'scored'
    );

    // Count by node type
    const byType = {};
    for (const node of nodes) {
      byType[node.nodeType] = (byType[node.nodeType] || 0) + 1;
    }

    // Count by public region
    const byRegion = {};
    for (const node of nodes) {
      const key = node.region?.precision === 'hidden' ? 'hidden' : node.region?.countryCode || 'unknown';
      byRegion[key] = (byRegion[key] || 0) + 1;
    }

    const activeNodes = nodes.filter(n => n.lifecycleStatus === 'active').length;

    // Count snapshots
    let snapshotCount = 0;
    for (const snapshots of this.reputation.snapshots.values()) {
      snapshotCount += snapshots.length;
    }

    return {
      protocol: {
        status: mainnet.status,
        network: mainnet.network
      },
      contributors: {
        count: profiles.length
      },
      contributions: {
        total: contributions.length,
        verified: verifiedContributions.length
      },
      nodes: {
        total: nodes.length,
        active: activeNodes,
        byType,
        byRegion
      },
      reputation: {
        profiles: profiles.length,
        snapshots: snapshotCount
      },
      sources: {
        mainnet: 'mpf-001',
        contributionPolicy: '002-draft-1',
        reputationPolicy: '003-draft-1',
        nodeRegistryPolicy: '004-draft-1'
      },
      generatedAt: new Date().toISOString()
    };
  }

  /**
   * Build deterministic network snapshot
   * @returns {Promise<object>} Network snapshot with fingerprint
   */
  async buildNetworkSnapshot() {
    const summary = await this.buildNetworkSummary();

    // Compute deterministic source fingerprints
    // Sort fields for determinism
    const summaryFingerprint = crypto.createHash('sha256')
      .update(JSON.stringify(summary, Object.keys(summary).sort()))
      .digest('hex');

    const canonicalSources = {
      mainnet: 'mpf-001-canonical',
      contributions: 'mpf-002-canonical',
      reputation: 'mpf-003-canonical',
      nodes: 'mpf-004-canonical'
    };

    const canonical = {
      sourceFingerprints: canonicalSources,
      summaryFingerprint
    };

    const canonicalString = JSON.stringify(canonical, Object.keys(canonical).sort());

    return {
      snapshotVersion: '1.0.0',
      snapshotId: `network-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`,
      sourceFingerprints: canonicalSources,
      generatedAt: new Date().toISOString(),
      snapshotFingerprint: `sha256:${crypto.createHash('sha256')
        .update(canonicalString)
        .digest('hex')}`
    };
  }

  /**
   * Build deterministic fingerprint for any data
   * @param {object} data - Data to fingerprint
   * @returns {string} SHA-256 fingerprint
   */
  buildFingerprint(data) {
    const canonical = JSON.stringify(data, Object.keys(data).sort());
    return `sha256:${crypto.createHash('sha256').update(canonical).digest('hex')}`;
  }
}

export default {
  MainnetService,
  ContributionService,
  ReputationService,
  NodeService,
  ProtocolApiService
};
