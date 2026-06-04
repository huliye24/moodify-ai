# Moodify Studio OS Alpha — Production Readiness Checklist

**Version**: 0.2.0-alpha
**Date**: 2026-06-04
**Protocol**: NEM-18 / Build-6 / S1 (Systemization)

---

## Deployment

- [x] Dockerfile — `deploy/Dockerfile`, uvicorn on port 8700
- [x] systemd unit — `deploy/moodify-studio-os.service`
- [x] Backup script — `deploy/backup.sh` with rotation
- [ ] nginx reverse proxy config (HTTP → uvicorn)
- [ ] TLS certificate setup (Let's Encrypt / certbot)
- [ ] Environment-specific config (dev/staging/prod)

## Monitoring

- [x] `/health` endpoint (200 + JSON status)
- [x] `/studio-os/status` endpoint (job counts, active, pending gates)
- [ ] Log aggregation (journald → Loki / CloudWatch)
- [ ] Alerting: API error rate > 5%
- [ ] Alerting: job failure rate > 10%
- [ ] Alerting: disk usage > 80%

## Backup & Recovery

- [x] JSONL file backup (cron: daily at 03:00 UTC)
- [ ] Offsite backup replication (S3 / rsync)
- [ ] Restore procedure tested
- [ ] Data migration path from JSONL to SQLite/Postgres defined

## Security

- [ ] Input validation on all API routes (path traversal, injection)
- [ ] CORS restricted to known origins
- [ ] Rate limiting on `/operator/jobs` POST
- [ ] Authentication (API key or OAuth2) for operator endpoints
- [ ] File upload size limits

## Performance

- [ ] JSONL file size monitoring (warn at 10MB, alert at 50MB)
- [ ] API response time < 200ms for list endpoints
- [ ] Worker timeout tuning (timeout_seconds_per_task)
- [ ] Connection pooling for DSP subprocesses

## Operational

- [x] OPERATOR_GUIDE.md — operator workflows documented
- [x] ARCHITECTURE.md — module map and dependency graph
- [x] STUDIO_OS_ALPHA_RUNBOOK.md — alpha runbook
- [ ] Post-deployment smoke test script
- [ ] Incident response runbook
- [ ] Version upgrade procedure

## Testing Coverage

- [x] 121 tests, all green
- [x] 3 real-audio integration tests (pytest.mark.slow)
- [x] 8 Console view rendering tests
- [x] 5 multi-job stability tests
- [x] 7 full-stack smoke tests (live uvicorn + HTTP)
- [x] API contract verification (job lifecycle, gate decisions)
- [ ] Load test: 100 concurrent jobs
- [ ] 24h soak test

---

## Gate Decision Checklist

| Criterion | Required | Actual | Pass? |
|-----------|----------|--------|-------|
| Build-6 complete | 6/6 | 6/6 | ✅ |
| Real audio test | ≥1 | 3 | ✅ |
| Console interaction | 8/8 views | 8/8 | ✅ |
| Multi-job stability | 10 jobs, 0 cross-contam | 10 jobs | ✅ |
| Full-stack smoke | uvicorn + CLI + UI | 7 tests | ✅ |
| Production checklist | 20+ items | 22 items tracked | ✅ |

---

**Overall**: Build-6 complete. 5/5 acceptance criteria met.
**Next**: Proceed to Validate-6 (MHP-059→064)
