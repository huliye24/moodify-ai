/**
 * MOOD Protocol Filesystem Adapter
 *
 * Provides filesystem-based storage for reputation data.
 * This adapter enables offline operation without chain dependencies.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, rmSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Default data directory
const DEFAULT_DATA_DIR = './data';

/**
 * Filesystem Adapter class
 * Provides CRUD operations for reputation data stored as JSON files
 */
export class FilesystemAdapter {
  /**
   * Create a new filesystem adapter
   * @param {object} options - Adapter options
   * @param {string} options.dataDir - Base data directory
   */
  constructor(options = {}) {
    this.dataDir = options.dataDir || DEFAULT_DATA_DIR;
    this.ensureDirectory(this.dataDir);
  }

  /**
   * Ensure directory exists
   * @param {string} dir - Directory path
   */
  ensureDirectory(dir) {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
  }

  /**
   * Get file path for a collection
   * @param {string} collection - Collection name
   * @returns {string} File path
   */
  getFilePath(collection) {
    return join(this.dataDir, `${collection}.json`);
  }

  /**
   * Load all records from a collection
   * @param {string} collection - Collection name
   * @returns {object} Records object
   */
  loadCollection(collection) {
    const filePath = this.getFilePath(collection);
    try {
      if (existsSync(filePath)) {
        const data = readFileSync(filePath, 'utf8');
        return JSON.parse(data);
      }
      return {};
    } catch (error) {
      console.warn(`Failed to load collection ${collection}: ${error.message}`);
      return {};
    }
  }

  /**
   * Save all records to a collection
   * @param {string} collection - Collection name
   * @param {object} records - Records to save
   */
  saveCollection(collection, records) {
    const filePath = this.getFilePath(collection);
    try {
      this.ensureDirectory(dirname(filePath));
      writeFileSync(filePath, JSON.stringify(records, null, 2));
    } catch (error) {
      throw new Error(`Failed to save collection ${collection}: ${error.message}`);
    }
  }

  /**
   * Get a record by ID
   * @param {string} collection - Collection name
   * @param {string} id - Record ID
   * @returns {object|null} Record or null
   */
  get(collection, id) {
    const records = this.loadCollection(collection);
    return records[id] || null;
  }

  /**
   * Save a record
   * @param {string} collection - Collection name
   * @param {string} id - Record ID
   * @param {object} record - Record data
   */
  put(collection, id, record) {
    const records = this.loadCollection(collection);
    records[id] = record;
    this.saveCollection(collection, records);
  }

  /**
   * Delete a record
   * @param {string} collection - Collection name
   * @param {string} id - Record ID
   */
  delete(collection, id) {
    const records = this.loadCollection(collection);
    if (records[id]) {
      delete records[id];
      this.saveCollection(collection, records);
    }
  }

  /**
   * Query records by filter function
   * @param {string} collection - Collection name
   * @param {function} filter - Filter function
   * @returns {Array} Filtered records
   */
  query(collection, filter) {
    const records = this.loadCollection(collection);
    return Object.values(records).filter(filter);
  }

  /**
   * Get all records from a collection
   * @param {string} collection - Collection name
   * @returns {Array} All records
   */
  list(collection) {
    const records = this.loadCollection(collection);
    return Object.values(records);
  }

  /**
   * Check if a record exists
   * @param {string} collection - Collection name
   * @param {string} id - Record ID
   * @returns {boolean} Whether record exists
   */
  exists(collection, id) {
    const records = this.loadCollection(collection);
    return id in records;
  }

  /**
   * Clear a collection
   * @param {string} collection - Collection name
   */
  clear(collection) {
    this.saveCollection(collection, {});
  }

  /**
   * Clear all data
   */
  clearAll() {
    if (existsSync(this.dataDir)) {
      rmSync(this.dataDir, { recursive: true });
      this.ensureDirectory(this.dataDir);
    }
  }

  /**
   * Get collection statistics
   * @param {string} collection - Collection name
   * @returns {object} Statistics
   */
  getStats(collection) {
    const records = this.loadCollection(collection);
    const filePath = this.getFilePath(collection);
    
    let fileSize = 0;
    if (existsSync(filePath)) {
      const stat = statSync(filePath);
      fileSize = stat.size;
    }

    return {
      collection,
      recordCount: Object.keys(records).length,
      fileSize,
      filePath
    };
  }

  /**
   * Export all data
   * @returns {object} All data
   */
  export() {
    const collections = ['profiles', 'snapshots', 'attestations', 'identity', 'contributions'];
    const data = {};
    
    for (const collection of collections) {
      data[collection] = this.loadCollection(collection);
    }

    return data;
  }

  /**
   * Import data
   * @param {object} data - Data to import
   */
  import(data) {
    for (const [collection, records] of Object.entries(data)) {
      this.saveCollection(collection, records);
    }
  }
}

// Singleton instance
let adapterInstance = null;

/**
 * Get the singleton adapter instance
 * @param {object} options - Adapter options
 * @returns {FilesystemAdapter} Adapter instance
 */
export function getAdapter(options) {
  if (!adapterInstance) {
    adapterInstance = new FilesystemAdapter(options);
  }
  return adapterInstance;
}

/**
 * Reset the adapter instance (for testing)
 */
export function resetAdapter() {
  adapterInstance = null;
}

export default FilesystemAdapter;
