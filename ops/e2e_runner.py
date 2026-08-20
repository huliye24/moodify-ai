#!/usr/bin/env python3
"""Cloud product E2E runner — MFY_CLOUD_PRODUCT_E2E_001.

Starts from the user entry (https://), never calls localhost to fake a
production pass. Two stages:

  --live        real public chain, read-only: website routes, Music
                discover→track→creator→Range, Ear health
  --local-ear   full Ear loop against a running local Ear API: upload →
                job → case → result (asserts manifest + authority state)

Exit 0 = all executed scenarios PASS; 1 = any FAIL; 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SITE = "https://rongjingmusic.com"
MUSIC = "https://rongjinwenchuan.xyz"
AUDIO_SAMPLE = f"{MUSIC}/audio/cadeau10-album1/je-ne-veux-pas-enfermer-ton-aujourdhui.wav"
# Live origin filters non-browser user agents (observed 2026-08-14: bare
# urllib -> 403, browser UA -> 200). Recorded as ops CAVEAT; nginx change
# requires authorization. The E2E runner therefore uses a browser UA.
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url: str, timeout: int = 15, headers: dict | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except Exception:
        return 0, b""

results: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    results.append((label, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))


def stage_live_read() -> None:
    print("== stage: live public chain (read-only) ==")
    # website routes (old placeholder origin serves 200; new site is a deploy gate)
    for route in ("/", "/ear.html", "/music.html", "/evidence.html", "/about.html", "/contact.html", "/privacy.html"):
        code, _ = get(f"{SITE}{route}")
        check(f"官网 {route}", code == 200, f"http {code}")

    # Music listener: discover → track detail → creator page → Range
    code, body = get(f"{MUSIC}/api/v1/music/catalogue")
    tracks = []
    if code == 200:
        try:
            tracks = json.loads(body).get("tracks", [])
        except ValueError:
            pass
    check("Music catalogue（匿名发现）", code == 200 and len(tracks) >= 1, f"{len(tracks)} tracks")
    if tracks:
        track_id = tracks[0]["id"]
        code, _ = get(f"{MUSIC}/t/{track_id}")
        check("Track 页面", code == 200, f"http {code}")
        code, _ = get(f"{MUSIC}/c/{tracks[0].get('creator_handle') or 'x'}")
        check("Creator 页面", code == 200, f"http {code}")
    code, body = get(AUDIO_SAMPLE, headers={"Range": "bytes=0-1023"})
    check("音频 Range（seek 前提）", code == 206 and len(body) == 1024, f"http {code} {len(body)}B")
    code, body = get(AUDIO_SAMPLE)
    check("音频全量（播放）", code == 200 and len(body) > 1024, f"http {code} {len(body)}B")

    # Ear read surface
    code, body = get(f"{SITE}/api/v1/health")
    check("Ear API health", code == 200 and b'"status":"ok"' in body, f"http {code}")


def stage_local_ear(api: str) -> None:
    print(f"== stage: full Ear loop against {api} ==")
    wav = Path("moodify-core-package/benchmarks/reference_audio/fixtures/clipped.wav")
    if not wav.is_file():
        check("fixture present", False, f"missing {wav}")
        return
    import mimetypes
    import uuid

    boundary = uuid.uuid4().hex
    audio = wav.read_bytes()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"e2e.wav\"\r\n"
        f"Content-Type: audio/wav\r\n\r\n".encode()
        + audio
        + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"prompt\"\r\n\r\nE2E loudness probe\r\n--{boundary}--\r\n".encode()
    )
    req = urllib.request.Request(
        f"{api}/api/v1/auditory/jobs", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            job = json.loads(resp.read()).get("job")
    except Exception as exc:  # noqa: BLE001
        check("上传→Job 创建", False, str(exc))
        return
    check("上传→Job 创建", job is not None and "job_id" in (job or {}), str(job))
    job_id = job["job_id"]

    status, deadline = "", time.time() + 240
    while time.time() < deadline:
        code, body = get(f"{api}/api/v1/auditory/jobs/{job_id}")
        if code == 200:
            status = json.loads(body).get("job", {}).get("status", "")
            if status in ("SUCCEEDED", "FAILED"):
                break
        time.sleep(5)
    check("Job 终态", status == "SUCCEEDED", status)

    code, body = get(f"{api}/api/v1/auditory/jobs/{job_id}/result")
    if code == 200:
        payload = json.loads(body)
        check("结果载荷完整", bool(payload.get("case_manifest")) and bool(payload.get("production_case")), "manifest+case")
        case = payload.get("production_case", {})
        check("authority_state 存在", bool(case.get("authority_state")), case.get("authority_state"))
    else:
        check("结果载荷完整", False, f"http {code}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="real public chain read-only E2E")
    parser.add_argument("--local-ear", metavar="API_URL", help="full Ear loop against a running local API")
    args = parser.parse_args()

    if args.live:
        stage_live_read()
    if args.local_ear:
        stage_local_ear(args.local_ear)
    if not (args.live or args.local_ear):
        parser.print_help()
        return 2

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n== E2E summary: {passed}/{len(results)} PASS ==")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
