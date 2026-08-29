# Rollback and Operations

## Git rollback

All Package 002 changes must be normal source-controlled changes.

Suggested commit:

```text
feat(protocol): add genesis wallet registration
```

No irreversible external action is allowed.

## Database rollback

Because this package adds new tables only, rollback should not require deleting existing product data.

If migration rollback is needed:
- prefer leaving unused new tables over destructive emergency deletion in production;
- document exact migration state.

Do not automatically drop tables containing real Genesis registrations.

## Operational notes

### Nonce expiry
Recommended TTL: 10 minutes unless existing auth infrastructure has a better standard.

### Terms version
Initial recommended identifier:

`genesis-v1`

This is a version identifier, not legal text itself.

### Participant status
Initial registration status:

`registered`

Future packages may introduce:
- reviewed
- eligible
- allocated
- distributed

Do not implement those workflows here beyond schema compatibility if useful.

### Monitoring
If the project already has logs/metrics, record:
- nonce endpoint failures;
- register verification failures;
- successful registrations;
- duplicate attempts.

Avoid high-cardinality signature logging.

## Human boundary

No human wallet signature should ever be automated beyond the participant's explicit message-sign action.
