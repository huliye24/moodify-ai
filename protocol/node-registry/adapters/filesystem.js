/**
 * MOOD Protocol Node Registry - Filesystem Adapter
 *
 * Provides filesystem-based storage for node registry data.
 * Enables offline operation without cloud dependencies.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, rmSync } from 'fs';
import { join, dirname } from 'path';

// Default data directory
const DEFAULT_DATA_DIR = './protocol/node-registry/data';

/**
 * Node Registry Filesystem Adapter
 */
export class NodeRegistryAdapter {
  /**
   * Create adapter
   * @param {object} options - Adapter options
   * @param {string} options.dataDir - Data directory
   */
  constructor(options = {}) {
    this.dataDir = options.dataDir || DEFAULT_DATA_DIR;
    this._ensureDirectory(this.dataDir);
  }

  /**
   * Ensure directory exists
   * @param {string} dir - Directory path
   */
  _ensureDirectory(dir) {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
  }

  /**
   * Get file path for collection
   * @param {string} collection - Collection name
   * @returns {string} File path
   */
  _getFilePath(collection) {
    return join(this.dataDir, `${collection}.json`);
  }

  /**
   * Load collection from file
   * @param {string} collection - Collection name
   * @returns {object} Records
   */
  _loadCollection(collection) {
    const filePath = this._getFilePath(collection);
    try {
      if (existsSync(filePath)) {
        const data = readFileSync(filePath, 'utf8');
        return JSON.parse(data);
      }
      return {};
    } catch (error) {
      console.warn(`Failed to load ${collection}: ${error.message}`);
      return {};
    }
  }

  /**
   * Save collection to file
   * @param {string} collection - Collection name
   * @param {object} records - Records to save
   */
  _saveCollection(collection, records) {
    const filePath = this._getFilePath(collection);
    this._ensureDirectory(dirname(filePath));
    writeFileSync(filePath, JSON.stringify(records, null, 2));
  }

  // ==================== Node Operations ====================

  /**
   * Save node record
   * @param {object} node - Node record
   */
  saveNode(node) {
    const nodes = this._loadCollection('nodes');
    nodes[node.nodeId] = node;
    this._saveCollection('nodes', nodes);
  }

  /**
   * Get node by ID
   * @param {string} nodeId - Node ID
   * @returns {object|null} Node record
   */
  getNode(nodeId) {
    const nodes = this._loadCollection('nodes');
    return nodes[nodeId] || null;
  }

  /**
   * Get all nodes
   * @returns {Array<object>} All node records
   */
  getAllNodes() {
    const nodes = this._loadCollection('nodes');
    return Object.values(nodes);
  }

  /**
   * Delete node
   * @param {string} nodeId - Node ID
   */
  deleteNode(nodeId) {
    const nodes = this._loadCollection('nodes');
    if (nodes[nodeId]) {
      delete nodes[nodeId];
      this._saveCollection('nodes', nodes);
    }
  }

  // ==================== Capability Operations ====================

  /**
   * Save capability manifest
   * @param {object} manifest - Capability manifest
   */
  saveCapabilityManifest(manifest) {
    const manifests = this._loadCollection('capabilities');
    manifests[manifest.manifestId] = manifest;
    this._saveCollection('capabilities', manifests);
  }

  /**
   * Get capability manifest by ID
   * @param {string} manifestId - Manifest ID
   * @returns {object|null} Capability manifest
   */
  getCapabilityManifest(manifestId) {
    const manifests = this._loadCollection('capabilities');
    return manifests[manifestId] || null;
  }

  /**
   * Get capabilities by node ID
   * @param {string} nodeId - Node ID
   * @returns {Array<object>} Capability manifests
   */
  getCapabilitiesByNode(nodeId) {
    const manifests = this._loadCollection('capabilities');
    return Object.values(manifests).filter(m => m.nodeId === nodeId);
  }

  // ==================== Heartbeat Operations ====================

  /**
   * Save heartbeat observation
   * @param {object} heartbeat - Heartbeat observation
   */
  saveHeartbeat(heartbeat) {
    const heartbeats = this._loadCollection('heartbeats');
    const nodeId = heartbeat.nodeId;

    if (!heartbeats[nodeId]) {
      heartbeats[nodeId] = [];
    }

    // Keep last 100 observations per node
    heartbeats[nodeId].push(heartbeat);
    if (heartbeats[nodeId].length > 100) {
      heartbeats[nodeId] = heartbeats[nodeId].slice(-100);
    }

    this._saveCollection('heartbeats', heartbeats);
  }

  /**
   * Get latest heartbeat for node
   * @param {string} nodeId - Node ID
   * @returns {object|null} Latest heartbeat
   */
  getLatestHeartbeat(nodeId) {
    const heartbeats = this._loadCollection('heartbeats');
    const nodeHeartbeats = heartbeats[nodeId];
    if (!nodeHeartbeats || nodeHeartbeats.length === 0) {
      return null;
    }
    return nodeHeartbeats[nodeHeartbeats.length - 1];
  }

  /**
   * Get heartbeat history for node
   * @param {string} nodeId - Node ID
   * @param {number} [limit] - Max records
   * @returns {Array<object>} Heartbeat history
   */
  getHeartbeatHistory(nodeId, limit = 100) {
    const heartbeats = this._loadCollection('heartbeats');
    const nodeHeartbeats = heartbeats[nodeId] || [];
    return nodeHeartbeats.slice(-limit);
  }

  // ==================== Verification Operations ====================

  /**
   * Save verification evidence
   * @param {object} evidence - Verification evidence
   */
  saveVerificationEvidence(evidence) {
    const evidence_list = this._loadCollection('verification_evidence');
    evidence_list[evidence.evidenceId] = evidence;
    this._saveCollection('verification_evidence', evidence_list);
  }

  /**
   * Get verification evidence by ID
   * @param {string} evidenceId - Evidence ID
   * @returns {object|null} Evidence
   */
  getVerificationEvidence(evidenceId) {
    const evidence_list = this._loadCollection('verification_evidence');
    return evidence_list[evidenceId] || null;
  }

  // ==================== Snapshot Operations ====================

  /**
   * Save registry snapshot
   * @param {object} snapshot - Registry snapshot
   */
  saveSnapshot(snapshot) {
    const snapshots = this._loadCollection('registry_snapshots');
    snapshots[snapshot.snapshotId] = snapshot;
    this._saveCollection('registry_snapshots', snapshots);
  }

  /**
   * Get snapshot by ID
   * @param {string} snapshotId - Snapshot ID
   * @returns {object|null} Snapshot
   */
  getSnapshot(snapshotId) {
    const snapshots = this._loadCollection('registry_snapshots');
    return snapshots[snapshotId] || null;
  }

  /**
   * Get latest snapshot
   * @returns {object|null} Latest snapshot
   */
  getLatestSnapshot() {
    const snapshots = this._loadCollection('registry_snapshots');
    const snapshotList = Object.values(snapshots);
    if (snapshotList.length === 0) return null;

    return snapshotList.sort((a, b) =>
      new Date(b.generatedAt) - new Date(a.generatedAt)
    )[0];
  }

  // ==================== Utility Operations ====================

  /**
   * Clear all data
   */
  clearAll() {
    if (existsSync(this.dataDir)) {
      rmSync(this.dataDir, { recursive: true });
      this._ensureDirectory(this.dataDir);
    }
  }

  /**
   * Export all data
   * @returns {object} All data
   */
  export() {
    return {
      nodes: this._loadCollection('nodes'),
      capabilities: this._loadCollection('capabilities'),
      heartbeats: this._loadCollection('heartbeats'),
      verification_evidence: this._loadCollection('verification_evidence'),
      registry_snapshots: this._loadCollection('registry_snapshots')
    };
  }

  /**
   * Import data
   * @param {object} data - Data to import
   */
  import(data) {
    for (const [collection, records] of Object.entries(data)) {
      this._saveCollection(collection, records);
    }
  }
}

// Singleton instance
let adapterInstance = null;

/**
 * Get singleton adapter instance
 * @param {object} options - Adapter options
 * @returns {NodeRegistryAdapter} Adapter
 */
export function getAdapter(options) {
  if (!adapterInstance) {
    adapterInstance = new NodeRegistryAdapter(options);
  }
  return adapterInstance;
}

/**
 * Reset adapter (for testing)
 */
export function resetAdapter() {
  adapterInstance = null;
}

export default NodeRegistryAdapter;
