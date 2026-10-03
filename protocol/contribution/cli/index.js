#!/usr/bin/env node

/**
 * MPF-002 Contribution Core CLI
 *
 * Developer-facing CLI for contribution operations.
 * Demonstrates the core without requiring a frontend or database.
 *
 * Usage:
 *   node cli/index.js create <json-file>
 *   node cli/index.js validate <json-file>
 *   node cli/index.js score <contribution-id> --scores <json>
 *   node cli/index.js inspect <contribution-id>
 *   node cli/index.js info
 */

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

const args = process.argv.slice(2);
const command = args[0];

// ─── Module imports ───────────────────────────────────────────────────────────

async function importModules() {
  const service = (await import('../src/service.js')).ContributionService;
  const { DuplicateGuard } = await import('../src/duplicate-guard.js');
  const { computeContentFingerprint } = await import('../src/fingerprint.js');
  const { validateContribution, validateContributor, checkForbiddenEconomicFields } = await import('../src/validate.js');
  const policy = await import('../src/policy.js');
  const { loadPolicy, checkMinimumEvidence, clearPolicyCache } = policy;
  const { canTransition } = await import('../src/state-machine.js');
  return { service, DuplicateGuard, computeContentFingerprint, validateContribution, validateContributor, checkForbiddenEconomicFields, loadPolicy, checkMinimumEvidence, clearPolicyCache, canTransition };
}

// ─── Commands ────────────────────────────────────────────────────────────────

async function cmdCreate(args) {
  const { service, DuplicateGuard, computeContentFingerprint } = await importModules();

  if (!args[0]) {
    console.error('Usage: create <contribution.json> [--submit]');
    process.exit(1);
  }

  const filePath = resolve(args[0]);
  let raw;
  try {
    raw = JSON.parse(readFileSync(filePath, 'utf8'));
  } catch (e) {
    console.error(`Failed to read JSON: ${e.message}`);
    process.exit(1);
  }

  const submit = args.includes('--submit');
  const svc = new ContributionService({ duplicateGuard: new DuplicateGuard() });

  const { contribution, errors } = svc.create(raw, submit);

  if (errors.length > 0) {
    console.error('❌ Creation failed with errors:');
    for (const err of errors) console.error(`  - ${err}`);
    process.exit(1);
  }

  console.log('✅ Contribution created successfully');
  console.log(`   ID:              ${contribution.contributionId}`);
  console.log(`   Status:          ${contribution.status}`);
  console.log(`   Fingerprint:     ${contribution.contentFingerprint}`);
  console.log(`   Category:        ${contribution.category}`);
  console.log(`   Contributor:     ${contribution.contributor.type}:${contribution.contributor.id}`);

  return contribution;
}

async function cmdValidate(args) {
  const {
    validateContribution, validateContributor,
    loadPolicy, checkMinimumEvidence, clearPolicyCache,
    computeContentFingerprint, checkForbiddenEconomicFields,
  } = await importModules();

  if (!args[0]) {
    console.error('Usage: validate <contribution.json>');
    process.exit(1);
  }

  const filePath = resolve(args[0]);
  let data;
  try {
    data = JSON.parse(readFileSync(filePath, 'utf8'));
  } catch (e) {
    console.error(`Failed to read JSON: ${e.message}`);
    process.exit(1);
  }

  // 1. Schema validation
  const contribResult = validateContribution(data);
  console.log(`Schema validation: ${contribResult.valid ? '✅ PASS' : '❌ FAIL'}`);
  if (!contribResult.valid) {
    for (const err of contribResult.errors) {
      console.error(`  - [${err.path}] ${err.message}`);
    }
  }

  // 2. Contributor validation
  if (data.contributor) {
    const contribIdResult = validateContributor(data.contributor);
    console.log(`Contributor:       ${contribIdResult.valid ? '✅ PASS' : '❌ FAIL'}`);
    if (!contribIdResult.valid) {
      console.error(`  - ${contribIdResult.error}`);
    }
  }

  // 3. Policy check
  clearPolicyCache();
  const policy = loadPolicy();
  const evidenceCheck = checkMinimumEvidence(data, policy);
  console.log(`Evidence (min ${evidenceCheck.required}): ${evidenceCheck.sufficient ? '✅ PASS' : '❌ FAIL'} (${evidenceCheck.actual}/${evidenceCheck.required})`);

  // 4. Fingerprint verification
  const { verifyFingerprint } = await import('../src/fingerprint.js');
  const fpMatch = verifyFingerprint(data);
  console.log(`Fingerprint:        ${fpMatch ? '✅ VERIFIED' : '⚠️  MISSING OR MISMATCH'}`);

  // 5. Economic field check
  const econFields = checkForbiddenEconomicFields(data);
  console.log(`Economic fields:   ${econFields.length === 0 ? '✅ NONE (clean)' : '❌ FOUND: ' + econFields.join(', ')}`);

  // 6. State machine validity
  const { ContributionStatus } = await import('../src/state-machine.js');
  const validStatuses = Object.values(ContributionStatus);
  if (validStatuses.includes(data.status)) {
    console.log(`Status:             ✅ '${data.status}' is a known state`);
  } else {
    console.log(`Status:             ❌ Unknown status: '${data.status}'`);
  }

  const allPass = contribResult.valid &&
    (!data.contributor || validateContributor(data.contributor).valid) &&
    evidenceCheck.sufficient && fpMatch && econFields.length === 0;

  console.log(`\n${allPass ? '✅ All checks passed' : '❌ Some checks failed'}`);
  process.exit(allPass ? 0 : 1);
}

async function cmdScore(args) {
  const { service: ContributionService, DuplicateGuard, clearPolicyCache } = await importModules();
  clearPolicyCache();

  // Parse --scores JSON from args
  const scoresIdx = args.indexOf('--scores');
  if (scoresIdx === -1 || !args[scoresIdx + 1]) {
    console.error('Usage: score <contribution-id> --scores \'{"contribution":{"value":80,...},...}\'');
    process.exit(1);
  }

  const contributionId = args[scoresIdx - 1] || args[0];
  const scoresJson = args[scoresIdx + 1];
  let dimensionScores;
  try {
    dimensionScores = JSON.parse(scoresJson);
  } catch (e) {
    console.error(`Invalid JSON for scores: ${e.message}`);
    process.exit(1);
  }

  const svc = new ContributionService({ duplicateGuard: new DuplicateGuard() });

  // For demo, create a verified contribution first
  const contribId = contributionId || 'demo-' + Date.now();
  console.log(`Scoring contribution: ${contribId}`);
  console.log('Note: In production, use the service with repository. This CLI demonstrates the API.');

  const result = svc.score(contribId, dimensionScores);
  if (result.error) {
    console.error(`❌ ${result.error}`);
    process.exit(1);
  }

  console.log('✅ Scored successfully');
  console.log(`   Status: ${result.contribution.status}`);
  console.log(`   Scores: ${JSON.stringify(result.contribution.scores, null, 2)}`);
}

async function cmdInspect(args) {
  const { service: ContributionService } = await importModules();
  const svc = new ContributionService();

  const id = args[0];
  if (!id) {
    console.error('Usage: inspect <contribution-id>');
    process.exit(1);
  }

  const record = svc._get(id);
  if (!record) {
    console.error(`Contribution not found: ${id}`);
    process.exit(1);
  }

  console.log('\n══════════════════════════════════════════');
  console.log(`  Contribution: ${record.contributionId}`);
  console.log('══════════════════════════════════════════');
  console.log(`Schema Version:    ${record.schemaVersion}`);
  console.log(`Status:            ${record.status}`);
  console.log(`Category:          ${record.category}`);
  console.log(`Contributor:       ${record.contributor.type}:${record.contributor.id}`);
  console.log(`Title:             ${record.title}`);
  console.log(`Submitted:         ${record.submittedAt}`);
  console.log(`Policy Version:    ${record.policyVersion}`);
  console.log(`Fingerprint:       ${record.contentFingerprint}`);
  console.log(`Evidence Count:    ${record.evidence ? record.evidence.length : 0}`);
  console.log(`Scores:            ${record.scores ? 'present' : 'none'}`);
  console.log(`Reputation Evidence: ${record.reputationEvidence ? 'present' : 'none'}`);
  if (record._transitions && record._transitions.length > 0) {
    console.log(`Transitions:`);
    for (const t of record._transitions) {
      console.log(`  - ${t.from} → ${t.to} (${t.at}${t.by ? ' by ' + t.by : ''})`);
    }
  }
  console.log('══════════════════════════════════════════\n');
}

async function cmdInfo(args) {
  const { loadPolicy } = await importModules();
  const { clearPolicyCache } = await import('../src/policy.js');
  clearPolicyCache();
  const policy = loadPolicy();

  console.log('\n══════════════════════════════════════════');
  console.log('  MPF-002 Contribution Core — Info');
  console.log('══════════════════════════════════════════');
  console.log(`Policy Version:    ${policy.policyVersion}`);
  console.log(`Policy Status:    ${policy.status}`);
  console.log(`Economic Convert: ${policy.economicConversionEnabled ? 'YES (⚠️)' : 'NO ✅'}`);
  console.log(`Weights Approved: ${policy.weights ? 'YES' : 'NO (aggregate will be null)'}`);
  console.log(`Independent Review: ${policy.requiresIndependentReview ? 'Required' : 'Optional'}`);
  console.log(`Finalized Immutable: ${policy.finalizedImmutable ? 'YES ✅' : 'NO'}`);
  console.log('\nDimensions:', policy.dimensions.join(', '));
  console.log('\nCategories:');
  for (const [cat, cfg] of Object.entries(policy.categories)) {
    const badge = cfg.eligible ? '✅' : '❌';
    console.log(`  ${badge} ${cat}: minEvidence=${cfg.minimumEvidence}`);
  }
  console.log('\nNO_CHAIN_WRITE_PERFORMED ✅');
  console.log('NO_TOKEN_DISTRIBUTION_PERFORMED ✅');
  console.log('══════════════════════════════════════════\n');
}

// ─── Entry point ─────────────────────────────────────────────────────────────

const COMMANDS = {
  create: cmdCreate,
  validate: cmdValidate,
  score: cmdScore,
  inspect: cmdInspect,
  info: cmdInfo,
};

if (!command || !COMMANDS[command]) {
  console.log(`
MPF-002 Contribution Core CLI

Usage:
  node cli/index.js info                      Show system info and policy
  node cli/index.js create <file.json>        Create a contribution
  node cli/index.js create <file.json> --submit  Create and submit
  node cli/index.js validate <file.json>      Validate a contribution record
  node cli/index.js inspect <contribution-id> Inspect a stored contribution
  node cli/index.js score <id> --scores '{...}' Score a contribution

Examples:
  node cli/index.js info
  node cli/index.js validate fixtures/valid-code-contribution.json
  node cli/index.js create fixtures/valid-code-contribution.json --submit
  node cli/index.js score mood-contrib-xxx --scores '{"contribution":{"value":80,"ruleId":"test.v1","evidenceIds":["e1"],"source":{}},"impact":{"value":75,"ruleId":"test.v1","evidenceIds":[],"source":{}},"quality":{"value":90,"ruleId":"test.v1","evidenceIds":[],"source":{}},"persistence":null,"early":null}'

Chain boundary: NO_CHAIN_WRITE_PERFORMED
Token boundary: NO_TOKEN_DISTRIBUTION_PERFORMED
`);
  process.exit(command ? 1 : 0);
}

try {
  await COMMANDS[command](args.slice(1));
} catch (err) {
  console.error(`❌ Command '${command}' failed: ${err.message}`);
  console.error(err.stack);
  process.exit(1);
}
