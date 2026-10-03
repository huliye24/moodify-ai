/**
 * MOOD Protocol Duplicate Guard
 *
 * Detects exact duplicates and flags cross-contributor duplicates.
 * Does not auto-accuse; suspicious records are flagged for review.
 */

import { buildContributorCategoryKey } from './ids.js';
import { computeContentFingerprint } from './fingerprint.js';

/**
 * The DuplicateGuard tracks fingerprints per contributor+category
 * to detect duplicates within and across contributors.
 */
export class DuplicateGuard {
  /**
   * @param {Map<string, string>} [existingFingerprints] - Pre-existing
   *   contribution fingerprints from storage, keyed by contribution ID.
   *   Format: contributionId → contentFingerprint
   */
  constructor(existingFingerprints = new Map()) {
    // contributionId → contentFingerprint
    this._byId = new Map(existingFingerprints);

    // contributor-category key → Map(contentFingerprint → contributionId)
    // Allows O(1) duplicate detection per contributor+category
    this._byContributorCategory = new Map();

    // contentFingerprint → [contributionId, ...] (cross-contributor tracking)
    this._byFingerprint = new Map();
  }

  /**
   * Register a contribution with the guard.
   *
   * @param {object} contribution - Contribution record
   */
  register(contribution) {
    const { contributionId, contributor, category } = contribution;
    const fingerprint = contribution.contentFingerprint ||
      computeContentFingerprint(contribution);

    // Index by ID
    this._byId.set(contributionId, fingerprint);

    // Index by contributor+category
    const ck = buildContributorCategoryKey(contributor, category);
    if (!this._byContributorCategory.has(ck)) {
      this._byContributorCategory.set(ck, new Map());
    }
    this._byContributorCategory.get(ck).set(fingerprint, contributionId);

    // Index by fingerprint for cross-contributor detection
    if (!this._byFingerprint.has(fingerprint)) {
      this._byFingerprint.set(fingerprint, []);
    }
    this._byFingerprint.get(fingerprint).push(contributionId);
  }

  /**
   * Check a new contribution for duplicates.
   *
   * @param {object} contribution - Proposed contribution
   * @returns {{ ok: boolean, reason?: string, flags?: object }}
   */
  check(contribution) {
    const { contributor, category } = contribution;
    const fingerprint = contribution.contentFingerprint ||
      computeContentFingerprint(contribution);
    const ck = buildContributorCategoryKey(contributor, category);

    // T1: Exact duplicate (same contributor + same category + same fingerprint)
    const ccMap = this._byContributorCategory.get(ck);
    if (ccMap && ccMap.has(fingerprint)) {
      const existingId = ccMap.get(fingerprint);
      return {
        ok: false,
        reason: 'EXACT_DUPLICATE',
        existingContributionId: existingId,
        message: `Contribution with identical content already exists: ${existingId}`,
      };
    }

    // T2: Cross-contributor duplicate — same fingerprint under different contributor
    const otherIds = this._byFingerprint.get(fingerprint);
    if (otherIds && otherIds.length > 0) {
      return {
        ok: true, // Not a hard rejection
        flags: {
          CROSS_CONTRIBUTOR_DUPLICATE: true,
          otherContributionIds: otherIds,
          message: `Content fingerprint matches ${otherIds.length} other contribution(s). Flagged for review.`,
        },
      };
    }

    return { ok: true };
  }

  /**
   * Remove a contribution from the guard (e.g., if it was rejected or superseded).
   *
   * @param {string} contributionId - Contribution ID to remove
   */
  unregister(contributionId) {
    const fingerprint = this._byId.get(contributionId);
    if (!fingerprint) return;

    this._byId.delete(contributionId);

    // Remove from contributor-category index
    for (const [, ccMap] of this._byContributorCategory) {
      if (ccMap.get(fingerprint) === contributionId) {
        ccMap.delete(fingerprint);
        break;
      }
    }

    // Remove from fingerprint index
    const list = this._byFingerprint.get(fingerprint);
    if (list) {
      const idx = list.indexOf(contributionId);
      if (idx !== -1) list.splice(idx, 1);
      if (list.length === 0) this._byFingerprint.delete(fingerprint);
    }
  }

  /**
   * Get all contribution IDs sharing the same content fingerprint.
   *
   * @param {string} fingerprint - Content fingerprint
   * @returns {string[]} Array of contribution IDs
   */
  getByFingerprint(fingerprint) {
    return this._byFingerprint.get(fingerprint) || [];
  }

  /**
   * Serialize guard state for persistence.
   *
   * @returns {object} Serializable state
   */
  serialize() {
    return {
      byId: [...this._byId.entries()],
      fingerprints: [...this._byFingerprint.entries()],
    };
  }
}
