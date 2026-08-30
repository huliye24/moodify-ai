/**
 * MOOD Protocol Contribution Validation
 *
 * JSON Schema validation for contribution records, evidence, and
 * reputation evidence. Uses Ajv with schema pre-registration so
 * $ref cross-references resolve correctly.
 */

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCHEMA_DIR = resolve(__dirname, '../schema');

// Economic field names that must not appear in any output
const FORBIDDEN_ECONOMIC_FIELDS = [
  'tokenAmount', 'payout', 'claimAmount', 'vesting',
  'token_price', 'reward_amount',
];

let _ajv = null;

function getAjv() {
  if (_ajv) return _ajv;

  _ajv = new Ajv({
    allErrors: true,
    strict: false,
    verbose: true,
  });
  addFormats(_ajv);

  // Register all schemas by $id so $ref resolution works
  const contribSchema = loadSchema('contribution.schema.json');
  const evidenceSchema = loadSchema('evidence.schema.json');
  const repSchema = loadSchema('reputation-evidence.schema.json');

  // Register evidence first (it's referenced by contribution)
  _ajv.addSchema(evidenceSchema);
  _ajv.addSchema(contribSchema);
  _ajv.addSchema(repSchema);

  return _ajv;
}

function loadSchema(filename) {
  const path = resolve(SCHEMA_DIR, filename);
  if (!existsSync(path)) throw new Error(`Schema not found: ${path}`);
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function validateContribution(contribution) {
  const ajv = getAjv();
  const validate = ajv.getSchema('mood://protocol/contribution/1.0.0');
  const valid = validate(contribution);
  return {
    valid: !!valid,
    errors: valid ? [] : formatErrors(validate.errors),
  };
}

export function validateEvidence(evidence) {
  const ajv = getAjv();
  const validate = ajv.getSchema('mood://protocol/evidence/1.0.0');
  const valid = validate(evidence);
  return {
    valid: !!valid,
    errors: valid ? [] : formatErrors(validate.errors),
  };
}

export function validateReputationEvidence(evidence) {
  const ajv = getAjv();
  const validate = ajv.getSchema('mood://protocol/reputation-evidence/1.0.0');
  const valid = validate(evidence);
  return {
    valid: !!valid,
    errors: valid ? [] : formatErrors(validate.errors),
  };
}

export function checkForbiddenEconomicFields(obj, path = '') {
  const found = [];
  if (obj === null || typeof obj !== 'object') return found;
  for (const key of Object.keys(obj)) {
    const fullPath = path ? `${path}.${key}` : key;
    if (FORBIDDEN_ECONOMIC_FIELDS.includes(key)) found.push(fullPath);
    const val = obj[key];
    if (val && typeof val === 'object') {
      found.push(...checkForbiddenEconomicFields(val, fullPath));
    }
  }
  return found;
}

export function validateContributor(contributor) {
  if (!contributor || typeof contributor !== 'object') {
    return { valid: false, error: 'Contributor must be an object' };
  }
  if (!contributor.type) {
    return { valid: false, error: 'Contributor type is required' };
  }
  const VALID_TYPES = ['wallet', 'github', 'protocol_id'];
  if (!VALID_TYPES.includes(contributor.type)) {
    return {
      valid: false,
      error: `Invalid contributor type: ${contributor.type}. Must be one of: ${VALID_TYPES.join(', ')}`,
    };
  }
  if (!contributor.id || typeof contributor.id !== 'string' || !contributor.id.trim()) {
    return { valid: false, error: 'Contributor id must be a non-empty string' };
  }
  if (contributor.type === 'wallet') {
    if (!contributor.id.startsWith('0x')) {
      return { valid: false, error: 'Wallet contributor id must start with 0x' };
    }
    if (contributor.id.length < 42) {
      return { valid: false, error: 'Wallet contributor id must be at least 42 chars' };
    }
  }
  return { valid: true, error: null };
}

function formatErrors(errors) {
  if (!errors) return [];
  return errors.map(e => ({
    path: e.instancePath || '/',
    message: e.message || 'Unknown error',
    keyword: e.keyword,
    params: e.params,
  }));
}
