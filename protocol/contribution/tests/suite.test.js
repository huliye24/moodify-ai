/**
 * MPF-002 Contribution Core Test Suite
 *
 * Covers T1–T18:
 * T1  Schema validation
 * T2  Canonical normalization
 * T3  Fingerprint determinism
 * T4  Fingerprint sensitivity
 * T5  Duplicate prevention
 * T6  Cross-contributor duplicate flag
 * T7  State transition guards
 * T8  Score guard
 * T9  Evidence guard
 * T10 Policy pinning
 * T11 Finalization immutability
 * T12 Reputation evidence determinism
 * T13 Economic-field prohibition
 * T14 No chain writes
 * T15 Offline operation
 * T16 Fixture coverage
 * T17 Full service lifecycle
 * T18 Self-review guard
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = resolve(__dirname, '../fixtures');

// ─── Module cache (synchronous after first load) ─────────────────────────────

const _modCache = {};

async function loadM(path) {
  if (_modCache[path]) return _modCache[path];
  const resolved = resolve(__dirname, '..', path);
  const ns = await import(`file://${resolved}`);
  _modCache[path] = ns;
  return ns;
}

// ─── Fixtures ────────────────────────────────────────────────────────────────

function loadFixture(name) {
  const path = resolve(FIXTURES_DIR, name);
  if (!existsSync(path)) throw new Error(`Fixture not found: ${name}`);
  return JSON.parse(readFileSync(path, 'utf8'));
}

// ─── Test framework ──────────────────────────────────────────────────────────

const results = [];
const _tests = [];

function test(name, fn) {
  _tests.push({ name, fn });
}

function assert(cond, msg = 'Assertion failed') {
  if (!cond) throw new Error(msg);
}

function assertEqual(a, b, msg = '') {
  if (a !== b) throw new Error(`${msg}\n  Expected: ${JSON.stringify(b)}\n  Actual:   ${JSON.stringify(a)}`);
}

// ═══════════════════════════════════════════════════════════════════════════════
// T1 — Schema validation
// ═══════════════════════════════════════════════════════════════════════════════

test('T1a — valid fixture passes schema', async () => {
  const { validateContribution } = await loadM('./src/validate.js');
  const record = loadFixture('valid-code-contribution.json');
  const { valid, errors } = validateContribution(record);
  assert(valid, `Schema validation failed: ${JSON.stringify(errors)}`);
});

test('T1b — malformed contributor fails contributor validation', async () => {
  const { validateContributor } = await loadM('./src/validate.js');
  const record = loadFixture('malformed-contributor.json');
  const { valid, error } = validateContributor(record.contributor);
  assert(!valid, 'Should have failed contributor validation');
  assert(error.includes('0x') || error.includes('wallet'), `Expected wallet address error, got: ${error}`);
});

test('T1c — missing evidence fails category minimum check', async () => {
  const { loadPolicy, checkMinimumEvidence, clearPolicyCache } = await loadM('./src/policy.js');
  clearPolicyCache();
  const record = loadFixture('missing-evidence.json');
  const policy = loadPolicy();
  const check = checkMinimumEvidence(record, policy);
  assert(!check.sufficient, 'Should not have sufficient evidence');
  assertEqual(check.required, 1);
  assertEqual(check.actual, 0);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T2 — Canonical normalization
// ═══════════════════════════════════════════════════════════════════════════════

test('T2 — equivalent JSON with different key order yields same canonical form', async () => {
  const { normalizeContribution } = await loadM('./src/normalize.js');
  const a = {
    schemaVersion: '1.0.0',
    contributor: { type: 'wallet', id: '0x123' },
    category: 'code',
    title: 'Test',
    description: 'Desc',
    submittedAt: '2026-08-29T00:00:00Z',
    evidence: [],
    policyVersion: '002-draft-1',
  };
  const b = {
    category: 'code',
    evidence: [],
    schemaVersion: '1.0.0',
    policyVersion: '002-draft-1',
    submittedAt: '2026-08-29T00:00:00Z',
    description: 'Desc',
    contributor: { id: '0x123', type: 'wallet' },
    title: 'Test',
  };
  const normA = normalizeContribution(a);
  const normB = normalizeContribution(b);
  assertEqual(normA, normB, 'Different key order should produce identical canonical form');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T3 — Fingerprint determinism
// ═══════════════════════════════════════════════════════════════════════════════

test('T3 — same immutable input yields same fingerprint over repeated runs', async () => {
  const { computeContentFingerprint } = await loadM('./src/fingerprint.js');
  const record = loadFixture('valid-code-contribution.json');
  const fp1 = computeContentFingerprint(record);
  const fp2 = computeContentFingerprint(record);
  const fp3 = computeContentFingerprint(record);
  assertEqual(fp1, fp2, 'Fingerprint must be deterministic');
  assertEqual(fp2, fp3, 'Fingerprint must be deterministic');
  assert(fp1.startsWith('sha256:'), `Fingerprint should start with sha256:, got: ${fp1}`);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T4 — Fingerprint sensitivity
// ═══════════════════════════════════════════════════════════════════════════════

test('T4 — changing material content changes fingerprint', async () => {
  const { computeContentFingerprint } = await loadM('./src/fingerprint.js');
  const base = {
    schemaVersion: '1.0.0',
    contributor: { type: 'wallet', id: '0x123' },
    category: 'code',
    title: 'Original title',
    description: 'Description',
    submittedAt: '2026-08-29T00:00:00Z',
    evidence: [],
    policyVersion: '002-draft-1',
  };
  const changed = { ...base, title: 'Modified title' };
  const fpBase = computeContentFingerprint(base);
  const fpChanged = computeContentFingerprint(changed);
  assert(fpBase !== fpChanged, 'Fingerprint must change when title changes');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T5 — Duplicate prevention
// ═══════════════════════════════════════════════════════════════════════════════

test('T5 — same contributor + category + fingerprint is rejected', async () => {
  const { DuplicateGuard } = await loadM('./src/duplicate-guard.js');
  const original = loadFixture('valid-code-contribution.json');
  const duplicate = loadFixture('duplicate-contribution.json');
  const guard = new DuplicateGuard();
  guard.register(original);
  const result = guard.check(duplicate);
  assert(!result.ok, 'Duplicate should be rejected');
  assertEqual(result.reason, 'EXACT_DUPLICATE');
  assert(result.existingContributionId !== undefined);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T6 — Cross-contributor duplicate flag
// ═══════════════════════════════════════════════════════════════════════════════

test('T6 — identical content under different contributor flags for review', async () => {
  const { DuplicateGuard } = await loadM('./src/duplicate-guard.js');
  const original = loadFixture('valid-docs-contribution.json');
  const crossDup = loadFixture('cross-contributor-duplicate.json');
  const guard = new DuplicateGuard();
  guard.register(original);
  const result = guard.check(crossDup);
  assert(result.ok, 'Cross-contributor is not a hard rejection');
  assert(result.flags !== undefined, 'Should have flags');
  assert(result.flags.CROSS_CONTRIBUTOR_DUPLICATE === true);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T7 — State transition guards
// ═══════════════════════════════════════════════════════════════════════════════

test('T7a — allowed transitions pass', async () => {
  const { canTransition } = await loadM('./src/state-machine.js');
  const allowed = [
    ['draft', 'submitted'],
    ['submitted', 'under_review'],
    ['under_review', 'verified'],
    ['under_review', 'rejected'],
    ['under_review', 'needs_more_evidence'],
    ['needs_more_evidence', 'under_review'],
    ['verified', 'scored'],
    ['scored', 'finalized'],
  ];
  for (const [from, to] of allowed) {
    const { valid, error } = canTransition(from, to);
    assert(valid, `Transition ${from} → ${to} should be valid: ${error}`);
  }
});

test('T7b — skipped and illegal transitions fail', async () => {
  const { canTransition } = await loadM('./src/state-machine.js');
  const illegal = [
    ['draft', 'verified'],
    ['draft', 'finalized'],
    ['submitted', 'verified'],
    ['rejected', 'verified'],
    ['finalized', 'scored'],
    ['verified', 'submitted'],
  ];
  for (const [from, to] of illegal) {
    const { valid, error } = canTransition(from, to);
    assert(!valid, `Transition ${from} → ${to} should be illegal: ${error}`);
  }
});

test('T7c — transition creates new object (immutable)', async () => {
  const { transition } = await loadM('./src/state-machine.js');
  const record = { status: 'draft', contributionId: 'test' };
  const { contribution } = transition(record, 'submitted');
  assert(record.status === 'draft', 'Original must not be mutated');
  assertEqual(contribution.status, 'submitted');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T8 — Score guard
// ═══════════════════════════════════════════════════════════════════════════════

test('T8a — scoring non-verified contribution fails', async () => {
  const { canScore } = await loadM('./src/state-machine.js');
  const nonScoreable = ['draft', 'submitted', 'under_review', 'needs_more_evidence', 'rejected', 'scored', 'finalized'];
  for (const status of nonScoreable) {
    const { allowed, error } = canScore(status);
    assert(!allowed, `Scoring in '${status}' should be forbidden: ${error}`);
  }
});

test('T8b — scoring verified contribution is allowed', async () => {
  const { canScore } = await loadM('./src/state-machine.js');
  const { allowed } = canScore('verified');
  assert(allowed, 'Scoring verified contribution should be allowed');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T9 — Evidence guard
// ═══════════════════════════════════════════════════════════════════════════════

test('T9 — contribution with no evidence cannot become verified', async () => {
  const { loadPolicy, checkMinimumEvidence, clearPolicyCache } = await loadM('./src/policy.js');
  clearPolicyCache();
  const record = loadFixture('missing-evidence.json');
  const policy = loadPolicy();
  const check = checkMinimumEvidence(record, policy);
  assert(!check.sufficient, 'No-evidence contribution should not pass minimum evidence');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T10 — Policy pinning
// ═══════════════════════════════════════════════════════════════════════════════

test('T10 — scored record pins exact policy version', async () => {
  const { buildReputationEvidence } = await loadM('./src/reputation-evidence.js');
  const contrib = {
    contributionId: 'test-contrib',
    contentFingerprint: 'sha256:' + 'a'.repeat(64),
  };
  const scores = {
    contribution: { value: 80, scale: '0-100', ruleId: 'test.v1', evidenceIds: [], source: {} },
    impact: { value: 75, scale: '0-100', ruleId: 'test.v1', evidenceIds: [], source: {} },
    quality: { value: 85, scale: '0-100', ruleId: 'test.v1', evidenceIds: [], source: {} },
    persistence: null,
    early: null,
  };
  const { reputationEvidence } = buildReputationEvidence(contrib, scores, null, '002-draft-1');
  assert(reputationEvidence !== null);
  assertEqual(reputationEvidence.policyVersion, '002-draft-1');
});

// ═══════════════════════════════════════════════════════════════════════════════
// T11 — Finalization immutability
// ═══════════════════════════════════════════════════════════════════════════════

test('T11a — finalized record is marked immutable', async () => {
  const { isImmutable, isTerminal } = await loadM('./src/state-machine.js');
  assert(isImmutable('finalized'), 'finalized must be immutable');
  assert(isImmutable('rejected'), 'rejected must be immutable');
  assert(isTerminal('finalized'), 'finalized must be terminal');
  assert(isTerminal('rejected'), 'rejected must be terminal');
});

test('T11b — mutation of finalized immutable fields fails', async () => {
  const { guardImmutableFields } = await loadM('./src/state-machine.js');
  const finalized = {
    status: 'finalized',
    title: 'Original',
    contributionId: 'test',
    schemaVersion: '1.0.0',
    contributor: { type: 'wallet', id: '0x1' },
    category: 'code',
    submittedAt: '2026-08-29T00:00:00Z',
    evidence: [],
    contentFingerprint: 'sha256:' + 'a'.repeat(64),
    supersedes: null,
  };
  const mutated = { ...finalized, title: 'Modified' };
  const { valid, error } = guardImmutableFields(finalized, mutated);
  assert(!valid, 'Should reject immutable field mutation');
  assert(error.includes('Immutable field'), `Expected immutable field error, got: ${error}`);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T12 — Reputation evidence determinism
// ═══════════════════════════════════════════════════════════════════════════════

test('T12 — same inputs produce same reputation evidence artifact', async () => {
  const { buildReputationEvidence } = await loadM('./src/reputation-evidence.js');
  const contrib = {
    contributionId: 'determinism-test',
    contentFingerprint: 'sha256:' + 'b'.repeat(64),
  };
  const scores = {
    contribution: { value: 90, scale: '0-100', ruleId: 'test.v1', evidenceIds: ['e1'], source: { type: 'human_review', id: 'r1' } },
    impact: { value: 85, scale: '0-100', ruleId: 'test.v1', evidenceIds: ['e2'], source: { type: 'human_review', id: 'r1' } },
    quality: { value: 88, scale: '0-100', ruleId: 'test.v1', evidenceIds: ['e3'], source: { type: 'human_review', id: 'r1' } },
    persistence: null,
    early: null,
  };
  const { reputationEvidence: re1 } = buildReputationEvidence(contrib, scores, null, '002-draft-1');
  const { reputationEvidence: re2 } = buildReputationEvidence(contrib, scores, null, '002-draft-1');
  assertEqual(re1.artifactFingerprint, re2.artifactFingerprint, 'Reputation evidence must be deterministic');
  assertEqual(re1.inputFingerprint, re2.inputFingerprint);
  assertEqual(re1.policyVersion, re2.policyVersion);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T13 — Economic-field prohibition
// ═══════════════════════════════════════════════════════════════════════════════

test('T13a — contribution schema rejects tokenAmount', async () => {
  const { validateContribution } = await loadM('./src/validate.js');
  const record = {
    schemaVersion: '1.0.0',
    contributionId: 'econ-test',
    contributor: { type: 'wallet', id: '0x1234567890123456789012345678901234567890' },
    category: 'code',
    title: 'Test',
    description: 'Test',
    submittedAt: '2026-08-29T00:00:00Z',
    evidence: [],
    status: 'submitted',
    policyVersion: '002-draft-1',
    contentFingerprint: 'sha256:' + 'c'.repeat(64),
    tokenAmount: 1000,
  };
  const { valid } = validateContribution(record);
  assert(!valid, 'Should reject tokenAmount field');
});

test('T13b — checkForbiddenEconomicFields detects payout', async () => {
  const { checkForbiddenEconomicFields } = await loadM('./src/validate.js');
  const found = checkForbiddenEconomicFields({ scores: { payout: 100 } });
  assert(found.includes('scores.payout'), `Should find payout, got: ${JSON.stringify(found)}`);
});

test('T13c — reputation evidence schema rejects tokenAmount', async () => {
  const { validateReputationEvidence } = await loadM('./src/validate.js');
  const bad = {
    contributionId: 'test',
    policyVersion: '002-draft-1',
    dimensions: { contribution: null, impact: null, quality: null, persistence: null, early: null },
    aggregate: null,
    status: 'scored',
    inputFingerprint: 'sha256:' + 'd'.repeat(64),
    artifactFingerprint: 'sha256:' + 'e'.repeat(64),
    tokenAmount: 1000,
  };
  const { valid } = validateReputationEvidence(bad);
  assert(!valid, 'Should reject tokenAmount in reputation evidence');
});

test('T13d — checkForbiddenEconomicFields detects all economic fields', async () => {
  const { checkForbiddenEconomicFields } = await loadM('./src/validate.js');
  const obj = {
    nested: { tokenAmount: 100, payout: 200, claimAmount: 300, vesting: 400, token_price: 5, reward_amount: 50 },
  };
  const found = checkForbiddenEconomicFields(obj);
  assert(found.includes('nested.tokenAmount'));
  assert(found.includes('nested.payout'));
  assert(found.includes('nested.claimAmount'));
  assert(found.includes('nested.vesting'));
});

// ═══════════════════════════════════════════════════════════════════════════════
// T14 — No chain writes (static scan)
// ═══════════════════════════════════════════════════════════════════════════════

test('T14 — no signing, transaction, or wallet-custody imports in core modules', async () => {
  const srcDir = resolve(__dirname, '../src');
  const FORBIDDEN = [
    'wallet_client', 'createWalletClient', 'createPublicClient',
    'sendTransaction', 'signTransaction', 'sendSignedTransaction',
    'privateKeyToAccount', 'mnemonicToAccount',
    'web3.eth.accounts.wallet', 'ethers.Wallet', 'ethers.Signer',
  ];
  const files = readdirSync(srcDir).filter(f => f.endsWith('.js'));
  const violations = [];
  for (const file of files) {
    const content = readFileSync(resolve(srcDir, file), 'utf8');
    for (const term of FORBIDDEN) {
      if (content.includes(term)) violations.push(`${file}: contains '${term}'`);
    }
  }
  assert(violations.length === 0, `Chain-write imports found:\n  ${violations.join('\n  ')}`);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T15 — Offline operation
// ═══════════════════════════════════════════════════════════════════════════════

test('T15 — no D1, no RPC, no fetch imports in core modules', async () => {
  const srcDir = resolve(__dirname, '../src');
  const FORBIDDEN_NET = [
    'cloudflare', 'd1', 'env.DB',
    'createClient',
    'fetch(', 'axios', 'got(',
  ];
  const files = readdirSync(srcDir).filter(f => f.endsWith('.js'));
  const violations = [];
  for (const file of files) {
    const content = readFileSync(resolve(srcDir, file), 'utf8');
    for (const term of FORBIDDEN_NET) {
      if (content.includes(term)) violations.push(`${file}: contains '${term}'`);
    }
  }
  assert(violations.length === 0, `Network/service dependencies found:\n  ${violations.join('\n  ')}`);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T16 — Fixture coverage
// ═══════════════════════════════════════════════════════════════════════════════

const REQUIRED_FIXTURES = [
  'valid-code-contribution.json', 'valid-docs-contribution.json',
  'valid-compute-contribution.json', 'missing-evidence.json',
  'malformed-contributor.json', 'duplicate-contribution.json',
  'invalid-state-transition.json', 'score-before-verify.json',
  'finalized-mutation.json', 'cross-contributor-duplicate.json',
  'policy-mismatch.json',
];

test('T16 — all required fixtures exist', async () => {
  const existing = readdirSync(FIXTURES_DIR).filter(f => f.endsWith('.json'));
  for (const required of REQUIRED_FIXTURES) {
    assert(existing.includes(required), `Missing fixture: ${required}`);
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// T17 — Full service lifecycle
// ═══════════════════════════════════════════════════════════════════════════════

test('T17 — full contribution lifecycle via service', async () => {
  const { ContributionService } = await loadM('./src/service.js');
  const { DuplicateGuard } = await loadM('./src/duplicate-guard.js');
  const { clearPolicyCache } = await loadM('./src/policy.js');
  clearPolicyCache();

  // Use in-memory repository for test isolation
  class InMemoryRepo {
    constructor() { this._map = new Map(); }
    save(c) { this._map.set(c.contributionId, c); }
    getById(id) { return this._map.get(id) || null; }
    delete(id) { this._map.delete(id); }
    listIds() { return [...this._map.keys()]; }
  }

  const repo = new InMemoryRepo();
  const guard = new DuplicateGuard();
  const svc = new ContributionService({ repository: repo, duplicateGuard: guard });

  const raw = {
    schemaVersion: '1.0.0',
    contributor: { type: 'wallet', id: '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' },
    category: 'code',
    title: 'Integration test contribution',
    description: 'Testing the full lifecycle.',
    evidence: [{
      evidenceId: 'evidence-int-001',
      type: 'git_commit',
      uri: null,
      digest: 'sha256:' + 'f'.repeat(64),
      observedAt: '2026-08-29T00:00:00Z',
      metadata: {},
      verification: { status: 'unverified' },
    }],
    policyVersion: '002-draft-1',
    status: 'submitted',
  };

  // Create
  const { contribution, errors } = svc.create(raw);
  assert(errors.length === 0, `Creation errors: ${errors.join('; ')}`);
  assertEqual(contribution.status, 'submitted');

  // Begin review
  const reviewResult = svc.beginReview(contribution.contributionId, 'reviewer-alice');
  assert(reviewResult.contribution !== null, reviewResult.error);
  assertEqual(reviewResult.contribution.status, 'under_review');

  // Verify
  const verifyResult = svc.verify(contribution.contributionId, 'reviewer-alice', 'Looks good');
  assert(verifyResult.contribution !== null, verifyResult.error);
  assertEqual(verifyResult.contribution.status, 'verified');

  // Score
  const scoreResult = svc.score(contribution.contributionId, {
    contribution: { value: 85, ruleId: 'manual.v1', evidenceIds: ['evidence-int-001'], source: { type: 'human_review', id: 'reviewer-alice' } },
    impact: { value: 80, ruleId: 'manual.v1', evidenceIds: ['evidence-int-001'], source: { type: 'human_review', id: 'reviewer-alice' } },
    quality: { value: 90, ruleId: 'manual.v1', evidenceIds: ['evidence-int-001'], source: { type: 'human_review', id: 'reviewer-alice' } },
    persistence: null,
    early: null,
  });
  assert(scoreResult.contribution !== null, scoreResult.error);
  assertEqual(scoreResult.contribution.status, 'scored');
  assert(scoreResult.contribution.scores !== null);
  assert(scoreResult.contribution.reputationEvidence !== null);

  // Finalize
  const finalizeResult = svc.finalize(contribution.contributionId);
  assert(finalizeResult.contribution !== null, finalizeResult.error);
  assertEqual(finalizeResult.contribution.status, 'finalized');
  assertEqual(finalizeResult.contribution.reputationEvidence.status, 'finalized');

  // Attempt to mutate finalized — should fail
  const mutateResult = svc.mutate(contribution.contributionId, { title: 'Hacked!' });
  assert(mutateResult.contribution === null, 'Finalized mutation should be rejected');
  assert(mutateResult.error.includes('IMMUTABILITY_VIOLATION'), `Got: ${mutateResult.error}`);
});

// ═══════════════════════════════════════════════════════════════════════════════
// T18 — Self-review guard
// ═══════════════════════════════════════════════════════════════════════════════

test('T18 — self-review is forbidden under current policy', async () => {
  const { ContributionService } = await loadM('./src/service.js');
  const { DuplicateGuard } = await loadM('./src/duplicate-guard.js');
  const { clearPolicyCache } = await loadM('./src/policy.js');
  clearPolicyCache();

  class InMemoryRepo {
    constructor() { this._map = new Map(); }
    save(c) { this._map.set(c.contributionId, c); }
    getById(id) { return this._map.get(id) || null; }
  }

  const svc = new ContributionService({ repository: new InMemoryRepo(), duplicateGuard: new DuplicateGuard() });
  const sameId = '0x1111111111111111111111111111111111111111';

  const { contribution } = svc.create({
    contributor: { type: 'wallet', id: sameId },
    category: 'code',
    title: 'Self-review test',
    description: 'Testing self-review guard.',
    evidence: [{
      evidenceId: 'e-self',
      type: 'git_commit',
      uri: null,
      digest: 'sha256:' + '1'.repeat(64),
      observedAt: '2026-08-29T00:00:00Z',
      metadata: {},
      verification: { status: 'unverified' },
    }],
    submittedAt: '2026-08-29T00:00:00Z',
  });

  svc.submit(contribution.contributionId);
  const result = svc.beginReview(contribution.contributionId, sameId);
  assert(result.contribution === null, 'Self-review should be rejected');
  assert(result.error.includes('SELF_REVIEW_FORBIDDEN'), `Got: ${result.error}`);
});

// ─── Run ─────────────────────────────────────────────────────────────────────

async function runTests() {
  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('  MPF-002 Contribution Core — Test Suite');
  console.log('═══════════════════════════════════════════════════════════\n');

  let pass = 0;
  let fail = 0;

  for (const { name, fn } of _tests) {
    try {
      await fn();
      results.push({ name, status: 'PASS' });
    } catch (err) {
      results.push({ name, status: 'FAIL', error: err.message });
    }
  }

  for (const r of results) {
    const icon = r.status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${r.name}`);
    if (r.status === 'FAIL') {
      console.log(`   └─ ERROR: ${r.error}`);
      fail++;
    } else {
      pass++;
    }
  }

  console.log(`\n───────────────────────────────────────────`);
  console.log(`  PASSED: ${pass}  |  FAILED: ${fail}  |  TOTAL: ${results.length}`);
  console.log(`───────────────────────────────────────────\n`);

  if (fail > 0) {
    console.error(`❌ ${fail} test(s) failed.`);
    process.exit(1);
  } else {
    console.log(`✅ All ${pass} tests passed.`);
    process.exit(0);
  }
}

runTests().catch(err => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
