# Compute Cost Baseline — MHP-252 | **Date**: 2026-06-04

## Current Single-Machine Costs

| Resource | Current Usage | Cost/Month (est.) |
|----------|--------------|-------------------|
| CPU | 15% peak (single core) | $20 (1 vCPU) |
| Memory | 180MB peak | Included |
| Disk | 49.5GB free | $5 (50GB SSD) |
| Network | Local-only | $0 |
| **Total (local)** | — | **~$25/month** |

## Cloud Scaling Estimates

| Workers | Tasks/Hour | Cost/Hour (est. $0.05/vCPU-hr) | Cost/Month |
|---------|-----------|-------------------------------|------------|
| 1 | ~180 | $0.05 | $36 |
| 2 | ~360 | $0.10 | $72 |
| 4 | ~720 | $0.20 | $144 |
| 8 | ~1440 | $0.40 | $288 |
| 16 | ~2880 | $0.80 | $576 |

## Cost Driver Analysis

| Driver | % of Cost | Optimization |
|--------|-----------|-------------|
| Compute time | 80% | Queue batching, task prioritization |
| Idle worker time | 15% | Auto-scale down on empty queue |
| Data transfer | 5% | Local artifact store, compress outputs |

## Breakeven

Local machine processes ~14,400 tasks/day (max). Cloud at 8 workers = ~34,560 tasks/day. Breakeven for needing cloud: queue depth > 500 pending tasks.
