# MHP-059: Dev Server Deployment — Docker + Systemd + Nginx

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / E (Execution)
**Depends on**: MHP-058 (Build-6 complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Studio OS Alpha has 45 API routes and an HTML console, but zero deployment configuration. The system can only be started manually with `uvicorn`. For Validate-6 production testing, we need it running as a persistent service accessible over HTTP.

## Goal

Create deployment configuration so a single command deploys the API server:

1. **Dockerfile** — containerize the API server
2. **systemd unit** — run as a system service
3. **nginx config** — reverse proxy with CORS
4. **Deploy script** — one-command deploy to dev server

## Non-Goals

- Don't set up CI/CD pipelines
- Don't configure auto-scaling
- Don't set up TLS (dev server only)

## Requirements

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY moodify_runtime/ ./moodify_runtime/
RUN pip install fastapi uvicorn pyyaml
CMD ["uvicorn", "moodify_runtime.operator_api:app", "--host", "0.0.0.0", "--port", "8700"]
```

### systemd unit
```ini
[Unit]
Description=Moodify Operator API
After=network.target

[Service]
Type=simple
User=moodify
WorkingDirectory=/opt/moodify
ExecStart=/opt/moodify/.venv/bin/uvicorn moodify_runtime.operator_api:app --host 0.0.0.0 --port 8700
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### nginx
```nginx
server {
    listen 80;
    server_name moodify.local;
    location / {
        proxy_pass http://127.0.0.1:8700;
        proxy_set_header Host $host;
    }
}
```

## Acceptance Criteria
- `docker build -t moodify-api .` succeeds
- `docker run -p 8700:8700 moodify-api` serves /health
- systemd unit starts the service
- Existing 107 tests still pass (deployment config is additive)

## Test Plan
```bash
docker build -t moodify-api . && docker run -d -p 8700:8700 moodify-api && curl http://localhost:8700/health
```
