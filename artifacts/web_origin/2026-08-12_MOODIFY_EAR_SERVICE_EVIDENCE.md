# Moodify Ear Service Deployment Evidence

## Outcome

`rongjingmusic.com` now submits audio to the canonical Moodify node queue and
runs the repository's Auditory Data Factory unattended. The former simulated
browser response has been replaced with queue polling and persisted results.

## Runtime architecture

- Nginx serves the workspace and proxies `/api/` to FastAPI on
  `127.0.0.1:8000`.
- `moodify-api.service` accepts bounded audio uploads and writes jobs into the
  existing SQLite `JobQueue`.
- `moodify-worker.service` is the single authoritative serial worker. It uses
  `moodify.data_factory.runner.run_production_case`; no second scanner or state
  machine was introduced.
- SQLite state and uploaded sources live below `/var/lib/moodify/state`.
- production cases and evidence live below `/var/lib/moodify/data_factory`.
- Both services are enabled at boot and restart on failure.

## Safety and recovery

- Upload limit: 50 MiB; retained queue cap: 500 jobs.
- Accepted extensions: WAV, MP3, FLAC, M4A, OGG, AAC.
- Nginx upload rate limit: 3 requests/minute/IP; API polling limit: 5/second/IP.
- Worker execution is serial and resource-gated.
- Failures retry at most three times, then retain typed operator evidence.
- Public job responses never expose source, output, or case filesystem paths.
- Releases are timestamped under `/opt/moodify/releases`; `/opt/moodify/current`
  is the active release symlink.

## Verification

- Local focused test suite: 52 queue, worker, API, Data Factory and
  compatibility tests passed.
- Auditory scan suite: 14 tests passed.
- Public `/api/v1/health` returned Moodify `1.0.0-rc.1`, identity
  `The Ear of AI`, and queue counts.
- API, worker, Nginx, and Cloudflare Tunnel were all active after restart.
- Production E2E job: `job_4fb8be6223ad40d1ba0da4970089dd93`.
- Evidence case: `case_1afb9047821f4ea399b2bc9c8b0d873b`.
- Case status: `ALGO_REVIEWED`; result ready: true.
- Algorithmic ranking returned: `SOURCE, A, B, C`.
- The case contains 62 files and approximately 6.9 MiB of retained evidence.

Five failed jobs remain intentionally in the queue ledger from deployment
diagnostics. They demonstrate bounded retry and failure preservation; they do
not block subsequent work.

## Compatibility findings resolved

- Python 3.10 dependency markers now select compatible NumPy/SciPy versions.
- A `StrEnum` compatibility implementation covers the declared Python 3.10
  runtime.
- FFmpeg 4.4 uses an evidence-recorded showspectrumpic fallback when it lacks
  the newer `drange`/`limit` options.
- Matplotlib is now a core dependency because the canonical comparison stage
  imports it in every production case.
