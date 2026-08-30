/**
 * MOOD Protocol Contribution Policy Loader
 *
 * Loads and validates contribution policy from config files.
 * Policy is read-only at runtime; version is pinned per contribution.
 */

import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_POLICY_PATH = resolve(__dirname, '../config/contribution-policy.draft.json');

let _policyCache = null;

/**
 * Load the contribution policy.
 * Caches the result for subsequent calls.
 *
 * @param {string} [policyPath] - Optional explicit policy path
 * @returns {object} Policy object
 */
export function loadPolicy(policyPath = null) {
  const path = policyPath || DEFAULT_POLICY_PATH;

  if (_policyCache && !policyPath) {
    return _policyCache;
  }

  if (!existsSync(path)) {
    throw new Error(`Policy file not found: ${path}`);
  }

  const policy = JSON.parse(readFileSync(path, 'utf8'));

  // Validate basic policy structure
  validatePolicyStructure(policy);

  if (!policyPath) {
    _policyCache = policy;
  }

  return policy;
}

/**
 * Validate basic policy structure.
 *
 * @param {object} policy - Policy object
 * @throws {Error} If policy structure is invalid
 */
function validatePolicyStructure(policy) {
  if (!policy.policyVersion) {
    throw new Error('Policy must have a policyVersion');
  }

  if (!Array.isArray(policy.dimensions) || policy.dimensions.length === 0) {
    throw new Error('Policy must define dimensions array');
  }

  if (typeof policy.categories !== 'object') {
    throw new Error('Policy must define categories map');
  }
}

/**
 * Check if a category is eligible for scoring under the current policy.
 *
 * @param {object} policy - Policy object
 * @param {string} category - Category name
 * @returns {{ eligible: boolean, minimumEvidence: number }}
 */
export function getCategoryPolicy(policy, category) {
  const cat = policy.categories[category];
  if (!cat) {
    return { eligible: false, minimumEvidence: 0 };
  }
  return {
    eligible: cat.eligible,
    minimumEvidence: cat.minimumEvidence || 0,
  };
}

/**
 * Check if a contribution has sufficient evidence for its category.
 *
 * @param {object} contribution - Contribution record
 * @param {object} policy - Policy object
 * @returns {{ sufficient: boolean, required: number, actual: number }}
 */
export function checkMinimumEvidence(contribution, policy) {
  const catPolicy = getCategoryPolicy(policy, contribution.category);
  const actualEvidence = contribution.evidence ?
    contribution.evidence.filter(e => e && e.evidenceId) : [];

  return {
    sufficient: actualEvidence.length >= catPolicy.minimumEvidence,
    required: catPolicy.minimumEvidence,
    actual: actualEvidence.length,
  };
}

/**
 * Get weights for aggregate computation.
 * Returns null if weights are not approved.
 *
 * @param {object} policy - Policy object
 * @returns {object|null} Weights map or null
 */
export function getWeights(policy) {
  if (policy.weights && policy.status !== 'draft') {
    return policy.weights;
  }
  return null;
}

/**
 * Clear the policy cache (useful for testing).
 */
export function clearPolicyCache() {
  _policyCache = null;
}
