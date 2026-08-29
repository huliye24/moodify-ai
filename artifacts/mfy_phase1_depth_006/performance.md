# Performance

Deterministic 48 kHz stereo cold runs:

| Duration | Wall | RTF | Cache |
|---:|---:|---:|---:|
| 30 s | 6.787 s | 0.22622 | 295,049 B |
| 180 s | 20.453 s | 0.11363 | 1,649,109 B |
| 600 s | 84.426 s | 0.14071 | 5,464,789 B |

Runtime and artifact size grow approximately linearly without pathological growth.
The identical 30-second warm run completed in 0.071 s (95.34x), with six cache hits,
zero decode and logical output equality.
