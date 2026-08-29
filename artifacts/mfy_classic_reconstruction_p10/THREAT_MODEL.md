# MFY-CR-P10 — Threat Model

**Date:** 2026-08-18
**Version:** v0.1
**Classification:** Architecture Document (not implementation)

---

## Threat Landscape

P10 protects **encrypted reconstruction results** — audio that has been processed by Moodify Cloud and must only be playable by the owning user on their registered device.

### What We Protect

| Asset | Sensitivity | At-Rest Protection | In-Transit Protection |
|---|---|---|---|
| Reconstruction result ciphertext | HIGH | AES-256-GCM per-object DEK | TLS |
| Wrapped DEK | HIGH | RSA-OAEP device public key | TLS |
| Device private key | CRITICAL | Android Keystore (TEE if available) | Never leaves device |
| Source audio during processing | MEDIUM | Transient, job-scoped | TLS upload |
| Job metadata | LOW | Server database (no PII in keys) | TLS |

---

## T01: Public URL Leakage

**Scenario:** Attacker obtains a result object URL (e.g., from logs, browser history, shared screenshot).

**Mitigation:**
- URLs are short-lived authenticated tokens (P08 contract), not static paths
- Object storage requires Bearer token + owner check
- Even with URL access, response is **AES-GCM ciphertext** — unplayable without wrapped DEK + device private key
- **Residual risk:** URL + token leak allows ciphertext download, but not plaintext recovery

**v0.1 Status:** ✅ DESIGNED — Ciphertext-only response enforced by server; client cannot decrypt without key material.

---

## T02: Cross-Account Access

**Scenario:** User A attempts to fetch User B's reconstruction result.

**Mitigation:**
- Every API call carries `owner_token` (P08) or device-scoped auth
- Server validates `owner_id` on every object request before returning ciphertext or wrapped keys
- Wrapped DEK is encrypted to **device-specific public key** — even if User A obtains the wrapped DEK, they cannot unwrap it without User B's device private key
- **Residual risk:** Compromised server can return any user's data (server-side authorization is software-enforced)

**v0.1 Status:** ✅ DESIGNED — Owner validation at API layer + per-device key wrapping.

---

## T03: Storage Leak

**Scenario:** Object storage bucket misconfiguration exposes files to public/anonymous read.

**Mitigation:**
- Files stored are **AES-GCM ciphertext** — public read yields garbage, not audio
- Wrapped DEK stored separately (database, not object storage)
- Even full bucket dump is useless without:
  1. Device private key (never in bucket)
  2. Per-object DEK (wrapped, needs private key)
- **Residual risk:** Attacker gets all ciphertexts but cannot decrypt any

**v0.1 Status:** ✅ DESIGNED — Encryption-at-rest renders storage leaks non-critical for audio content.

---

## T04: Database Leak

**Scenario:** Database backup/exfiltration reveals metadata and wrapped keys.

**Mitigation:**
- Database contains: object_id, owner_id, wrapped_DEK, metadata
- **Does NOT contain:** private keys, plaintext DEKs, audio bytes
- Wrapped DEK is RSA-OAEP encrypted — useless without device private key (which is not in DB)
- Metadata is minimal (codec, duration, chunk_count — no PII beyond owner_id)
- **Residual risk:** Attacker learns which users have reconstructions, approximate durations, key IDs

**v0.1 Status:** ✅ DESIGNED — No secret key material in database.

---

## T05: Log Leak

**Scenario:** Logs contain tokens, keys, file paths, or audio references.

**Mitigation (P10 Logging Rules):**
- **FORBIDDEN in logs:** private key, DEK, raw auth token, raw audio bytes, full local content URI, plaintext storage path
- **ALLOWED in logs:** object_id, job_id, key_id, chunk_index, status, algorithm version, error class
- Structured logging with redaction rules
- **Residual risk:** Developer accidentally adds debug log with sensitive data (process/culture control)

**v0.1 Status:** ⚠️ POLICY DEFINED — Code review + linter rule needed for enforcement.

---

## T06: Device Compromise

**Scenario:** Android device is rooted or malware gains elevated privileges.

**Mitigation:**
- Private key stored in **Android Keystore** with `setUserAuthenticationRequired(true)` if hardware-backed
- On TEE-equipped devices: key extraction is extremely difficult even with root
- **Honest admission:** On non-TEE / rooted devices, privileged malware CAN extract the key
- This is a **PARTIAL protection** scenario per P10 security boundary
- **Residual risk:** Full device compromise = game over for any client-side crypto (fundamental limit)

**v0.1 Status:** ⚠️ PARTIAL — Hardware-dependent. TEE devices: strong. Rooted non-TEE: weak.

---

## T07: Server Compromise During Processing

**Scenario:** Attacker gains code execution on the processing node while a job is running.

**Mitigation:**
- Plaintext source/result exists only in **job-scoped workspace** with TTL-based cleanup
- DEK exists only in process memory during encryption finalization
- No swap-to-disk of key material (best-effort; Python GC limits guarantees)
- After finalization: plaintext deleted, DEK dropped from memory
- **Residual risk:** Live compromise during the ~30s encryption window exposes one job's plaintext

**v0.1 Status:** ⚠️ PARTIAL — Time-bounded exposure window. Cannot prevent live-memory extraction.

---

## T08: Backup Leak

**Scenario:** Server snapshot/backup contains plaintext that should have been deleted.

**Mitigation:**
- P10 requires **BACKUP_AND_SNAPSHOT_REVIEW** audit document
- Encryption finalization MUST complete before job marked SUCCESS
- Cleanup on success/failure/cancellation is mandatory
- Backup retention policy must be verified separately
- **Residual risk:** Snapshot taken between "encrypt" and "delete plaintext" captures transient state

**v0.1 Status:** ❌ BLOCKED — Requires ops access to backup systems for audit.

---

## T09: Retry Residue

**Scenario:** Failed/retried jobs leave behind source audio, candidate plaintexts, or intermediate files.

**Mitigation:**
- All job workspaces are **job-scoped** with unique directory per attempt
- Cleanup runs on: success, failure, cancellation, timeout
- Retry creates new workspace; old workspace cleaned independently
- Stale workspace scanner (cron) for orphaned directories > 24h
- **Residual race condition:** Crash between "write file" and "register cleanup" leaves orphan

**v0.1 Status:** ✅ DESIGNED — Job-scoped workspace + cleanup hooks + stale scanner.

---

## T10: Offline Cache Extraction

**Scenario:** User or other app extracts cached decrypted audio from app-private storage.

**Mitigation:**
- **No full-file plaintext cache** (P10 §21)
- Streaming/chunked decryption: only current chunk in memory
- If temporary compatibility mode needed: app-private encrypted cache with lifecycle cleanup
- No MediaStore indexing, no share URI, no world-readable files
- **Residual risk:** Rooted device can extract app-private files; this overlaps with T06

**v0.1 Status:** ✅ DESIGNED — Streaming decryption avoids persistent plaintext cache.

---

## Summary Table

| ID | Scenario | Severity | v0.1 Mitigation | Residual Risk |
|---|---|---|---|---|
| T01 | Public URL leakage | MEDIUM | Ciphertext-only response | URL+token → ciphertext download (unplayable) |
| T02 | Cross-account access | HIGH | Owner auth + per-device key wrap | Server compromise bypasses auth |
| T03 | Storage leak | HIGH | Encryption-at-rest | Full bucket dump = useless ciphertext |
| T04 | Database leak | MEDIUM | No keys in DB | Metadata exposure (non-audio) |
| T05 | Log leak | MEDIUM | Redaction rules | Human error in development |
| T06 | Device compromise | CRITICAL | Android Keystore / TEE | Fundamental limit on compromised device |
| T07 | Server compromise | CRITICAL | Job-scoped workspace + TTL | Live-memory window during processing |
| T08 | Backup leak | HIGH | Finalization-before-success | Snapshot timing race condition |
| T09 | Retry residue | MEDIUM | Job-scoped cleanup | Orphaned workspace on crash |
| T10 | Cache extraction | MEDIUM | Streaming decrypt, no file cache | Overlaps with T06 (root) |

## What P10 Does NOT Protect Against

- Screen/audio capture by legitimate device owner (fundamental)
- Analog output recording (microphone near speaker)
- Copyright ownership questions (legal, not technical)
- DRM-equivalent anti-copy guarantees (explicitly out of scope)
- Nation-state actors with device-level persistence (beyond v0.1 scope)

---

## Verdict

P10 v0.1 threat model provides **strong protection against opportunistic and infrastructure-level attacks** (T01-T04, T09-T10). It provides **partial protection against determined adversaries** (T05-T07) with honest acknowledgment of residual risks. It **cannot protect against device-level compromise** (T06) or insider/server-level attacks (T07-T08) — these require organizational controls beyond cryptography.
