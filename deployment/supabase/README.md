# deployment/supabase — cloud authority for Identity / Account / Personal History

**Contract:** [`protocol/mips/MIP-0003-personal-identity-history.md`](../../protocol/mips/MIP-0003-personal-identity-history.md)
**Status:** code + migrations + policies are in the repository; **real deployment is `DEPLOYMENT_BLOCKED`**
(no project credentials, no database reachable from this machine).

```text
supabase/
  README.md                    this file
  migrations/0001_identity_history.sql   tables, RLS, owner boundary, controlled deletion
  tests/local_shim.sql         vanilla-PostgreSQL stand-in for auth.users / auth.uid() — local only
  tests/rls_two_users.sql      the two-user isolation suite (11 checks)
  tests/run_rls_tests.js       runner: applies migrations + suite, or SKIPS LOUDLY (exit 2)
```

## What lives in the cloud (and what never does)

Allowed: `title`, `duration_ms`, `completion_mode`, `selected`, `completed_at`, `inscription`,
coarse history events, `work_id`, `audio_availability='LOCAL_ONLY'`.

Never: audio bytes, stems, MIDI, scores, reports/evidence, spectra, Mix Graph parameters,
local absolute paths, source hashes, tokens/OTP/magic-link URLs, terminal logs, search or
listening history. The desktop side asserts this on every outgoing payload
(`moodify-desktop/src/history-sync/schema.js`, tests in `scripts/test-sync.js`).

## Applying the migrations

Supabase CLI (when available):

```bash
supabase link --project-ref <ref>
supabase db push
```

Plain PostgreSQL (local throwaway database only):

```bash
psql -v ON_ERROR_STOP=1 -d "$DATABASE_URL" -f tests/local_shim.sql
psql -v ON_ERROR_STOP=1 -d "$DATABASE_URL" -f migrations/0001_identity_history.sql
```

Never apply `tests/local_shim.sql` to a Supabase project — it would replace the platform's
`auth.uid()`. The runner refuses to do so.

## RLS suite

```bash
DATABASE_URL=postgres://… node deployment/supabase/tests/run_rls_tests.js
```

Exit codes: `0` = suite reported PASS (owner isolation verified) · `1` = the suite ran and
failed · `2` = **it could not run** (no psql, no credentials, or a refused shim target).
Exit `2` is intentional: "could not verify" must never be mistaken for "verified". While it
returns `2`, Phase 3A is `DEPLOYMENT_BLOCKED`.

The suite proves, with two real users (A and B) and a fresh transaction rolled back at the end:

1. an unauthenticated session sees zero rows and cannot insert;
2. A sees exactly its own row;
3. A cannot read B's row by guessing `work_id`;
4. A cannot update or delete B's row (0 rows affected);
5. a spoofed `user_id` on insert is rejected by `with check`;
6. the same `request_id` pushed twice yields exactly one event (idempotency);
7. deleting a work leaves a tombstone; re-claiming is refused (no resurrection);
8. `export_account_data()` contains only the caller's rows, with no audio/path/hash material;
9. `delete_account(uuid)` is not executable by `anon` or `authenticated` — only `service_role`;
10. `anon` has no table privileges on any of the four tables;
11. all fixtures are removed inside the rolled-back transaction.

## Secrets

`MOODIFY_SUPABASE_URL` and `MOODIFY_SUPABASE_ANON_KEY` are **public client configuration**
(the anon key is designed to be shippable; RLS is what protects the data). The **service-role
key must never** appear in the desktop app, the renderer, tests or this repository — the only
place it may live is the deployment environment that calls `delete_account(uuid)`.
