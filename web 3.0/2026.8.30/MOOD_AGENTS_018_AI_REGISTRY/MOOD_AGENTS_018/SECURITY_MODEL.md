# SECURITY MODEL

Threats:

- prompt injection
- malicious tool input
- command injection
- SSRF
- secret leakage
- privilege escalation
- forged proof
- fake heartbeat
- runaway task loops
- cost explosion
- unauthorized code changes
- autonomous funds movement

## Hard boundaries

018 Agent MUST NOT:

- hold private keys
- sign transactions
- transfer funds
- approve token spend
- deploy production token
- change reputation without review
- approve contribution without human authority
