#!/usr/bin/env python3
"""
Local helper: redact sensitive query parameters in URLs before saving logs/reports.
No network access.
"""
from __future__ import annotations
import argparse
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

SENSITIVE = {
    "signature","sig","token","access_token","authorization",
    "x-oss-signature","x-oss-credential","x-oss-security-token",
    "x-amz-signature","x-amz-credential","x-amz-security-token"
}

def redact(url: str) -> str:
    p = urlsplit(url)
    query = []
    for k, v in parse_qsl(p.query, keep_blank_values=True):
        if k.lower() in SENSITIVE or "signature" in k.lower() or "token" in k.lower() or "credential" in k.lower():
            v = "***REDACTED***"
        query.append((k, v))
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), p.fragment))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    args = ap.parse_args()
    print(redact(args.url))

if __name__ == "__main__":
    main()
