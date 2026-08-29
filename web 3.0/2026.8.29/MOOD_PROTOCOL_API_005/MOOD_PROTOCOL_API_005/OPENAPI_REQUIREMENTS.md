# OpenAPI Requirements

Codex should generate an OpenAPI 3.x document or equivalent framework-native schema.

Minimum documented tags:

```text
Health
Protocol
Contributions
Contributors
Reputation
Nodes
Network
```

Each endpoint must declare:

- method/path
- public/restricted status
- parameters
- request body if any
- success schema
- error schema
- pagination if applicable

The API contract must not include economic actions in MPF-005.
