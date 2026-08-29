# Codex Execution Prompt

Execute **Moodify Protocol Genesis 006 — Contribution Network** inside the existing Moodify repository.

## Dependencies

Confirm Packages 001–005 or equivalent foundations exist.

Reuse:
- official MOOD config;
- Genesis Participant identity;
- admin authorization;
- exact MOOD arithmetic patterns;
- distribution/export conventions where appropriate.

Official MOOD:
- BNB Smart Chain
- chainId 56
- `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- 18 decimals

## Mission

Build the first contribution economy:

`Task → Submission → Review → Reputation → Pending MOOD Reward`

No automatic token transfer.

## Mandatory audit before editing

1. Read repository instructions/canon.
2. Inspect git status and preserve unrelated work.
3. Inspect active web routing/design system.
4. Inspect Genesis Participant schema.
5. Inspect Package 003 admin authorization.
6. Inspect Package 004 exact token arithmetic/export utilities.
7. Inspect Package 005 airdrop/distribution boundaries.
8. Inspect existing task/content/upload/GitHub integrations.
9. Inspect D1/Drizzle migration conventions.
10. Identify build/test commands.

Do not create duplicate identity or admin systems.

## Public implementation

Create `/contribute`.

Implement:
- contribution introduction;
- active task catalog;
- task detail;
- submission form;
- evidence input;
- My Contributions;
- Reputation summary;
- Pending MOOD summary.

Clearly label MOOD rewards as:
`Pending allocation`
until they are actually included/distributed.

## Admin implementation

Create `/admin/contributions` using existing secure admin gate.

Implement:
- task management;
- review queue;
- submission detail;
- request changes;
- approve;
- reject;
- final Reputation points;
- final pending MOOD reward;
- audit timeline.

## Data model

Add/extend:
- contribution_tasks
- contribution_submissions
- contribution_review_events
- reputation_events
- reward_events

Use additive migrations.

## Exact rewards

Use exact integer/string arithmetic.

No JS floats for token units.

Store atomic MOOD values using 18 decimals.

## Status models

Task:
- draft
- active
- paused
- completed
- archived

Submission:
- submitted
- under_review
- changes_requested
- approved
- rejected
- withdrawn

Reward:
- pending
- included_in_snapshot
- distributed
- cancelled

Validate transitions server-side.

## Reputation

Reputation is non-transferable/off-chain.

Append events.

Do not directly overwrite a score without corresponding event.

If a cached aggregate exists, keep it consistent and test it.

## Anti-abuse

Do not reward:
- trading volume;
- buying MOOD;
- holding MOOD;
- fake referrals;
- wallet farming;
- social spam.

Add practical controls for:
- duplicate submissions;
- max approvals;
- rate limiting;
- reviewer authorization;
- self-review prevention where possible.

## Evidence

Support:
- text;
- URL list;
- GitHub PR/commit links;
- existing Moodify report/test IDs if current repo supports them.

Do not build a new unsafe file-storage system just for this package.

## Reward export

Provide deterministic pending-reward export for future distribution.

Suggested command:

```bash
npm run contributions:rewards-export
```

Output must contain:
- participant number;
- wallet;
- reward MOOD;
- reward atomic;
- source reward event IDs.

No admin notes/signatures/nonces.

## Documentation

Create:

`docs/protocol/CONTRIBUTION_NETWORK.md`

## Hard prohibitions

Do not:
- auto-transfer MOOD;
- sign transactions;
- request private keys;
- deploy new reward contracts;
- implement staking/yield;
- make token-price promises;
- use market price in reward formula;
- auto-approve high-value rewards solely with AI;
- overwrite Genesis allocation with contribution rewards.

## Tests

At minimum:

- public active-task filtering;
- unregistered submission denied;
- valid participant submission;
- invalid status transition;
- review authorization;
- self-review guard;
- changes requested lifecycle;
- approval generates reputation event;
- approval generates pending reward event;
- exact reward arithmetic;
- negative reward rejected;
- cached reputation consistency;
- duplicate submission policy;
- max approval enforcement;
- cancelled reward audit;
- reward export deterministic;
- export privacy;
- Genesis allocation untouched.

Run:
- migration validation;
- lint;
- typecheck;
- tests;
- production build.

## Completion output

Return:

1. audit findings;
2. schema changes;
3. task/submission/reward status models;
4. Reputation model;
5. reward exactness model;
6. anti-abuse controls;
7. public routes;
8. admin routes;
9. reward export format;
10. tests/build results;
11. screenshots;
12. files changed;
13. git diff summary;
14. exact safety statement:

`No automatic MOOD token transfer, wallet signature, smart-contract deployment, liquidity operation, market-manipulation mechanism, or private-key handling was performed by this task.`

## Stop conditions

Stop for human confirmation if:
- contribution reward policy conflicts with canon;
- an automated token transfer is requested;
- production reward ceiling/policy is required but undefined;
- a new admin identity model would weaken security;
- destructive migration required;
- wallet/private key/signing required.
