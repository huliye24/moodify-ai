/**
 * MOOD Protocol Contribution Service
 *
 * Single authoritative entry point for contribution operations.
 *
 * NO_CHAIN_WRITE_PERFORMED
 * NO_TOKEN_DISTRIBUTION_PERFORMED
 */

import { generateContributionId, normalizeContributorId } from './ids.js';
import { computeContentFingerprint } from './fingerprint.js';
import { normalizeContribution } from './normalize.js';
import {
  validateContribution,
  validateContributor,
  checkForbiddenEconomicFields,
} from './validate.js';
import {
  transition,
  canScore,
  canFinalize,
  isImmutable,
  guardImmutableFields,
  ContributionStatus,
} from './state-machine.js';
import { DuplicateGuard } from './duplicate-guard.js';
import { scoreContribution, validateScores } from './score.js';
import { buildReputationEvidence, finalizeReputationEvidence } from './reputation-evidence.js';
import { loadPolicy, checkMinimumEvidence } from './policy.js';

export { ContributionStatus };

export class ContributionService {
  /**
   * @param {object} opts
   * @param {object} [opts.repository] - Storage adapter (e.g. FilesystemRepository)
   * @param {DuplicateGuard} [opts.duplicateGuard]
   * @param {string} [opts.policyPath]
   */
  constructor(opts = {}) {
    this.repository = opts.repository || null;
    this.duplicateGuard = opts.duplicateGuard || new DuplicateGuard();
    this.policyPath = opts.policyPath || null;
  }

  get policy() {
    return loadPolicy(this.policyPath);
  }

  /**
   * Create a new contribution record.
   * Computes content fingerprint, generates deterministic ID.
   *
   * @param {object} raw - Raw contribution data
   * @param {boolean} [submit=false] - Immediately transition to submitted
   * @returns {{ contribution: object, errors: Array }}
   */
  create(raw, submit = false) {
    const errors = [];

    // 1. Normalize contributor
    const contributorId = normalizeContributorId(raw.contributor.id);
    const normalizedContributor = { ...raw.contributor, id: contributorId };

    // 2. Canonical fields
    const schemaVersion = raw.schemaVersion || '1.0.0';
    const submittedAt = raw.submittedAt || new Date().toISOString();
    const category = raw.category;
    const policyVersion = raw.policyVersion || this.policy.policyVersion;

    // 3. Compute content fingerprint
    const contentFingerprint = computeContentFingerprint({
      schemaVersion,
      contributor: normalizedContributor,
      category,
      title: raw.title,
      description: raw.description,
      submittedAt,
      evidence: raw.evidence || [],
      policyVersion,
      supersedes: raw.supersedes || null,
    });

    // 4. Generate deterministic ID
    const contributionId = generateContributionId({
      schemaVersion,
      contributorType: normalizedContributor.type,
      contributorId: normalizedContributor.id,
      category,
      contentFingerprint,
      submittedAt,
    });

    // 5. Build the record
    let record = {
      schemaVersion,
      contributor: normalizedContributor,
      category,
      title: raw.title,
      description: raw.description,
      submittedAt,
      evidence: raw.evidence || [],
      policyVersion,
      supersedes: raw.supersedes || null,
      contributionId,
      status: ContributionStatus.DRAFT,
      contentFingerprint,
      review: null,
      scores: null,
      reputationEvidence: null,
      _createdAt: new Date().toISOString(),
      _transitions: [],
    };

    // 6. Validate schema (strip internal fields)
    const schemaRecord = { ...record };
    delete schemaRecord._createdAt;
    delete schemaRecord._transitions;
    delete schemaRecord._duplicateFlags;
    const contribValidation = validateContribution(schemaRecord);
    if (!contribValidation.valid) {
      errors.push(...contribValidation.errors.map(e => `contribution: ${e.message}`));
    }

    // 7. Validate contributor identity
    const contribIdValidation = validateContributor(normalizedContributor);
    if (!contribIdValidation.valid) {
      errors.push(`contributor: ${contribIdValidation.error}`);
    }

    // 8. Economic field check
    const econFields = checkForbiddenEconomicFields(record);
    if (econFields.length > 0) {
      errors.push(`economic fields forbidden: ${econFields.join(', ')}`);
    }

    // 9. Duplicate check
    const dupResult = this.duplicateGuard.check(record);
    if (!dupResult.ok) {
      errors.push(`duplicate: ${dupResult.message}`);
    }
    if (dupResult.flags) {
      record._duplicateFlags = dupResult.flags;
    }

    if (errors.length > 0) {
      return { contribution: record, errors };
    }

    // 10. Optional submit transition
    if (submit || raw.status === ContributionStatus.SUBMITTED) {
      const { contribution: submitted, error: txError } = transition(
        record, ContributionStatus.SUBMITTED,
      );
      if (txError) {
        errors.push(`transition: ${txError}`);
      } else {
        record = submitted;
      }
    }

    // 11. Register and save
    this.duplicateGuard.register(record);
    this._save(record);

    return { contribution: record, errors };
  }

  submit(contributionId) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };
    const { contribution, error: txError } = transition(record, ContributionStatus.SUBMITTED);
    if (txError) return { contribution: null, error: txError };
    this._save(contribution);
    return { contribution };
  }

  beginReview(contributionId, reviewerId) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    if (this.policy.requiresIndependentReview) {
      const contribNorm = normalizeContributorId(record.contributor.id);
      const reviewerNorm = normalizeContributorId(reviewerId);
      if (contribNorm === reviewerNorm) {
        return {
          contribution: null,
          error: 'SELF_REVIEW_FORBIDDEN: contributor and reviewer cannot be the same identity under current policy',
        };
      }
    }

    const { contribution, error: txError } = transition(
      record, ContributionStatus.UNDER_REVIEW, { reviewerId },
    );
    if (txError) return { contribution: null, error: txError };
    this._save(contribution);
    return { contribution };
  }

  verify(contributionId, reviewerId, reviewNotes = null) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    const evidenceCheck = checkMinimumEvidence(record, this.policy);
    if (!evidenceCheck.sufficient) {
      return {
        contribution: null,
        error: `INSUFFICIENT_EVIDENCE: requires ${evidenceCheck.required} evidence, has ${evidenceCheck.actual}`,
      };
    }

    const review = { reviewerId, reviewedAt: new Date().toISOString(), notes: reviewNotes };
    let updated = { ...record, review };

    const { contribution, error: txError } = transition(
      updated, ContributionStatus.VERIFIED, { reviewerId },
    );
    if (txError) return { contribution: null, error: txError };

    this._save(contribution);
    return { contribution };
  }

  reject(contributionId, reviewerId, reason) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    const review = { reviewerId, reviewedAt: new Date().toISOString(), notes: reason, outcome: 'rejected' };
    let updated = { ...record, review };

    const { contribution, error: txError } = transition(
      updated, ContributionStatus.REJECTED, { reviewerId, reason },
    );
    if (txError) return { contribution: null, error: txError };

    this.duplicateGuard.unregister(contributionId);
    this._save(contribution);
    return { contribution };
  }

  requestMoreEvidence(contributionId, reviewerId, reason) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    const review = { reviewerId, reviewedAt: new Date().toISOString(), notes: reason, outcome: 'needs_more_evidence' };
    let updated = { ...record, review };

    const { contribution, error: txError } = transition(
      updated, ContributionStatus.NEEDS_MORE_EVIDENCE, { reviewerId, reason },
    );
    if (txError) return { contribution: null, error: txError };

    this._save(contribution);
    return { contribution };
  }

  score(contributionId, dimensionScores) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    const { allowed, error: scoreError } = canScore(record.status);
    if (!allowed) return { contribution: null, error: `SCORE_GUARD: ${scoreError}` };

    const scoresResult = scoreContribution(record, dimensionScores, this.policy);
    const scoresValidation = validateScores(scoresResult.scores);
    if (!scoresValidation.valid) {
      return {
        contribution: null,
        error: `Invalid scores: ${scoresValidation.errors.join('; ')}`,
      };
    }

    const evidenceResult = buildReputationEvidence(
      record, scoresResult.scores, scoresResult.aggregate, this.policy.policyVersion,
    );
    if (evidenceResult.error) {
      return { contribution: null, error: `Reputation evidence: ${evidenceResult.error}` };
    }

    let updated = {
      ...record,
      scores: scoresResult.scores,
      reputationEvidence: evidenceResult.reputationEvidence,
    };

    const { contribution, error: txError } = transition(updated, ContributionStatus.SCORED);
    if (txError) return { contribution: null, error: txError };

    this._save(contribution);
    return { contribution };
  }

  finalize(contributionId) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    const { allowed, error: finalizeError } = canFinalize(record.status);
    if (!allowed) return { contribution: null, error: `FINALIZE_GUARD: ${finalizeError}` };

    const { evidence: finalizedEvidence, error: evidenceError } =
      finalizeReputationEvidence(record.reputationEvidence);
    if (evidenceError) {
      return { contribution: null, error: `Finalize evidence: ${evidenceError}` };
    }

    let updated = { ...record, reputationEvidence: finalizedEvidence };
    const { contribution, error: txError } = transition(updated, ContributionStatus.FINALIZED);
    if (txError) return { contribution: null, error: txError };

    this._save(contribution);
    return { contribution };
  }

  mutate(contributionId, updates) {
    const record = this._get(contributionId);
    if (!record) return { contribution: null, error: `Not found: ${contributionId}` };

    if (isImmutable(record.status)) {
      return {
        contribution: null,
        error: `IMMUTABILITY_VIOLATION: cannot mutate record in '${record.status}' status`,
      };
    }

    const proposed = { ...record, ...updates };
    const guardResult = guardImmutableFields(record, proposed);
    if (!guardResult.valid) {
      return { contribution: null, error: guardResult.error };
    }

    this._save(proposed);
    return { contribution: proposed };
  }

  // ─── Repository helpers ────────────────────────────────────────────────────

  _get(id) {
    if (!this.repository) return null;
    return this.repository.getById(id);
  }

  _save(contribution) {
    if (this.repository) this.repository.save(contribution);
  }
}
