# API Versioning

## API version

Start with:

```text
v1
```

## Breaking change

Examples:

- renaming response fields
- changing ID format
- changing meaning of status
- removing routes
- changing visibility semantics

must not happen silently within v1.

## Policy version vs API version

These are different:

```text
API version = transport/contract
Policy version = protocol rule set
```

Example:

```text
API v1
Reputation policy 003-draft-1
Node policy 004-draft-1
```

Do not conflate them.

## Deprecation

Future deprecated fields/routes should have explicit deprecation notes and migration path.
