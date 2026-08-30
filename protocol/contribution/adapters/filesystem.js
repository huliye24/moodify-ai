/**
 * MOOD Protocol Filesystem Contribution Repository
 *
 * JSON-file based storage adapter.
 * Storage-agnostic: the core domain has no dependency on this adapter.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync, readdirSync } from 'fs';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_DATA_DIR = resolve(__dirname, '../../data/contribution');

/**
 * Filesystem repository for contribution records.
 * Stores each contribution as a separate JSON file keyed by contribution ID.
 */
export class FilesystemRepository {
  /**
   * @param {string} [dataDir] - Directory for contribution JSON files
   */
  constructor(dataDir = DEFAULT_DATA_DIR) {
    this.dataDir = dataDir;
    this._ensureDirectory();
  }

  _ensureDirectory() {
    if (!existsSync(this.dataDir)) {
      mkdirSync(this.dataDir, { recursive: true });
    }
  }

  /**
   * Get a contribution by ID.
   *
   * @param {string} contributionId - Contribution ID
   * @returns {object|null} Contribution record or null
   */
  getById(contributionId) {
    const path = this._filePath(contributionId);
    if (!existsSync(path)) return null;
    try {
      return JSON.parse(readFileSync(path, 'utf8'));
    } catch {
      return null;
    }
  }

  /**
   * Save a contribution record.
   *
   * @param {object} contribution - Contribution record
   */
  save(contribution) {
    const path = this._filePath(contribution.contributionId);
    writeFileSync(path, JSON.stringify(contribution, null, 2), 'utf8');
  }

  /**
   * Delete a contribution record.
   *
   * @param {string} contributionId - Contribution ID
   */
  delete(contributionId) {
    const path = this._filePath(contributionId);
    if (existsSync(path)) {
      unlinkSync(path);
    }
  }

  /**
   * List all contribution IDs.
   *
   * @returns {string[]} Array of contribution IDs
   */
  listIds() {
    try {
      const files = readdirSync(this.dataDir);
      return files
        .filter(f => f.endsWith('.json'))
        .map(f => f.replace(/\.json$/, ''));
    } catch {
      return [];
    }
  }

  /**
   * Load all contributions from storage.
   *
   * @returns {Map<string, object>} Map of contributionId → record
   */
  loadAll() {
    const map = new Map();
    try {
      const files = readdirSync(this.dataDir);
      for (const file of files) {
        if (!file.endsWith('.json')) continue;
        const id = file.replace(/\.json$/, '');
        const record = this.getById(id);
        if (record) map.set(id, record);
      }
    } catch {
      // Directory may not exist yet
    }
    return map;
  }

  /**
   * Build the file path for a contribution ID.
   *
   * @param {string} contributionId - Contribution ID
   * @returns {string} Absolute file path
   */
  _filePath(contributionId) {
    // Sanitize: remove path separators
    const safe = contributionId.replace(/[/\\:]/g, '_');
    return join(this.dataDir, `${safe}.json`);
  }
}
