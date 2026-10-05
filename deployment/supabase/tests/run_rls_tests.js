#!/usr/bin/env node
/**
 * RLS suite runner — Phase 3A (`deployment/supabase/tests/rls_two_users.sql`).
 *
 * What it does:
 *   • finds a PostgreSQL client (`psql`) and a database URL (`DATABASE_URL` or `SUPABASE_DB_URL`);
 *   • applies `tests/local_shim.sql` **only** for a locally reachable throwaway database
 *     (never for a Supabase host, and never without `MOODIFY_RLS_SHIM_OK=1`);
 *   • applies `migrations/*.sql` in filename order, then the RLS suite;
 *   • passes only when the suite prints its PASS line, and fails loudly otherwise.
 *
 * What it does when the tooling or credentials are missing:
 *   it prints `SKIPPED (reason)` and exits with code 2 — deliberately **not** 0, so that no
 *   pipeline, script or human can mistake "could not run" for "the policies are verified".
 *   The Phase 3A delivery is `DEPLOYMENT_BLOCKED` until this exits 0 with real evidence.
 *
 * Run: node deployment/supabase/tests/run_rls_tests.js
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const HERE = __dirname;
const MIGRATIONS = path.join(HERE, '..', 'migrations');

function skip(reason) {
  console.log('RLS suite: SKIPPED (' + reason + ')');
  console.log('  → owner boundary is NOT verified by this run; Phase 3A stays DEPLOYMENT_BLOCKED.');
  console.log('  → to run it: provide a throwaway PostgreSQL/Supabase database and either');
  console.log('    psql on PATH, then:  DATABASE_URL=postgres://… node deployment/supabase/tests/run_rls_tests.js');
  process.exit(2);
}

const psql = spawnSync('psql', ['--version'], { encoding: 'utf8' });
if (psql.error || psql.status !== 0) {
  skip('no psql on PATH (Supabase CLI/psql are not installed in this environment)');
}
const version = (psql.stdout || '').trim();

const url = process.env.DATABASE_URL || process.env.SUPABASE_DB_URL || '';
if (!url) skip('no DATABASE_URL / SUPABASE_DB_URL (no credentials for any project)');

const isLocal = /@(localhost|127\.0\.0\.1|\[::1\])[:/]/.test(url);
const isSupabaseHost = /supabase\.(co|in|net)/.test(url);
if (isSupabaseHost && process.env.MOODIFY_RLS_SHIM_OK === '1') {
  skip('refusing to run the vanilla-PostgreSQL shim against a Supabase host');
}
const useShim = isLocal && !isSupabaseHost;

function run(label, args, input) {
  const res = spawnSync('psql', args, {
    encoding: 'utf8',
    input,
    env: process.env,
  });
  if (res.status !== 0) {
    console.error(`\n✗ ${label} failed (exit ${res.status})`);
    console.error((res.stdout || '').trim().slice(-4000));
    console.error((res.stderr || '').trim().slice(-4000));
    process.exit(1);
  }
  return res.stdout || '';
}

console.log(`RLS suite: ${version}`);
console.log(`  database: ${url.replace(/\/\/[^@]*@/, '//***@')}`);
console.log(`  shim:     ${useShim ? 'local_shim.sql (throwaway local database)' : 'none (real Supabase schema)'}`);

const base = ['-v', 'ON_ERROR_STOP=1', '-q', '-X', '-d', url];
if (useShim) run('local shim', [...base, '-f', path.join(HERE, 'local_shim.sql')]);

const migrations = fs.readdirSync(MIGRATIONS).filter((n) => n.endsWith('.sql')).sort();
if (!migrations.length) skip('no migrations found in deployment/supabase/migrations');
for (const name of migrations) {
  run(`migration ${name}`, [...base, '-f', path.join(MIGRATIONS, name)]);
  console.log(`  applied ${name}`);
}

const out = run('rls_two_users.sql', [...base, '-f', path.join(HERE, 'rls_two_users.sql')]);
const passed = /rls suite: PASS/.test(out);
console.log(out.trim());
if (!passed) {
  console.error('\n✗ the RLS suite ran but did not report PASS — owner isolation is NOT verified');
  process.exit(1);
}
console.log('\n✓ RLS suite PASS — two-user isolation verified against a real database');
