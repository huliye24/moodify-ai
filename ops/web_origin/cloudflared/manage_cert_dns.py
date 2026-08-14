#!/usr/bin/env python3
"""Small DNS helper using cloudflared's local origin certificate.

It never prints the embedded API token. Intended for deployment evidence and
for removing test records created by the tunnel provisioning command.
"""

import argparse
import base64
import json
import urllib.parse
import urllib.request


def credentials(path: str) -> dict:
    pem = open(path, encoding="utf-8").read().splitlines()
    payload = "".join(line.strip() for line in pem if not line.startswith("---"))
    return json.loads(base64.b64decode(payload + "==="))


def api(token: str, method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + path,
        data=data,
        method=method,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if not result.get("success"):
        raise SystemExit(json.dumps(result.get("errors", [])))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("list", "delete"))
    parser.add_argument("name")
    parser.add_argument("--cert", default="/root/.cloudflared/cert.pem")
    args = parser.parse_args()
    creds = credentials(args.cert)
    zone_id, token = creds["zoneID"], creds["apiToken"]
    query = urllib.parse.urlencode({"name": args.name, "per_page": 100})
    records = api(token, "GET", f"/zones/{zone_id}/dns_records?{query}")["result"]
    if args.action == "list":
        for record in records:
            print(record["id"], record["type"], record["name"], record["content"], record["proxied"])
        return
    for record in records:
        api(token, "DELETE", f"/zones/{zone_id}/dns_records/{record['id']}")
        print("deleted", record["type"], record["name"])


if __name__ == "__main__":
    main()
