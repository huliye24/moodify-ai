"""listen_demo_render.py — 一次性离线渲染 Listen Demo 公开对比音频。

目的:
  把 apps/web/assets/cadeau10-album1.json 里的 5 首原声跑 MoodifyDSPChain,
  落 wav 到部署路径,产出公开 manifest(姐妹文件)的 sidecar。

约束:
  - 离线,无 Cloud Pipeline / Job authority / State machine 介入
  - 单 Profile v1 (保守档:可见的中频人声 / 适度低温暖 / 谨慎混响)
  - 落 wav 进部署路径,不进 git
  - 落 manifest sidecar (sha256 / bytes / durationSeconds) 进 git
  - 任何最终进入公开对比的 wav,须经真人试听确认
    "听得出区别" 后再同步公开 manifest 到 apps/web/assets/

输入:
  --input-dir        Cadeau10 原声所在目录(默认 apps/web/assets/cadeau10-album1.json 同级)
  --output-dir       wav 输出目录(默认 LA /opt/moodify/music-media/audio/cadeau10-album1-moodify)
  --manifest-input   apps/web/assets/cadeau10-album1.json
  --manifest-output  manifest sidecar 输出位置
  --profile          listen-demo-profile-v1(保守档)

执行:
  python -m scripts.listen_demo_render
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.processing.pedalboard_chain import MoodifyDSPChain


LISTEN_DEMO_PROFILE_V1: dict[str, float] = {
    "P01_vocal_presence_freq": 3200.0,
    "P02_vocal_presence_gain": 1.5,
    "P03_vocal_presence_q": 0.9,
    "P04_proximity_low_freq": 180.0,
    "P05_proximity_low_gain": 0.8,
    "P06_compression_ratio": 1.6,
    "P07_compression_attack": 18.0,
    "P08_compression_release": 160.0,
    "P09_compression_threshold": -22.0,
    "P10_reverb_room_size": 0.18,
    "P11_reverb_dry_wet": 0.18,
    "P12_reverb_width": 0.6,
    "P13_harmonic_drive": 0.0,
    "P14_high_shelf_freq": 11000.0,
    "P15_high_shelf_gain": 0.5,
}


@dataclass
class TrackResult:
    id: str
    title: str
    source_file: str
    source_sha256: str
    source_bytes: int
    output_file: str
    output_sha256: str
    output_bytes: int
    duration_seconds: float
    public_url: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def render_track(input_path: Path, output_path: Path, profile: dict[str, float]) -> dict:
    audio, sr = sf.read(str(input_path), always_2d=False, dtype="float32")
    chain = MoodifyDSPChain()
    processed, fingerprint, conservation = chain.process_with_audit(audio, sr, params=profile)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), processed, sr, subtype="PCM_16")
    return {
        "sr": int(sr),
        "duration_seconds": round(float(len(processed) / sr), 3),
        "fingerprint_thd_db": round(float(fingerprint.thd_db), 4),
        "fingerprint_transient_preservation": round(float(fingerprint.transient_preservation), 4),
        "fingerprint_spectral_centroid_shift_hz": round(float(fingerprint.spectral_centroid_shift), 2),
        "conservation_pass": bool(conservation.passed),
        "conservation_residual_db": round(float(conservation.delta_l_residual_db), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("/opt/moodify/music-media/audio/cadeau10-album1"),
        help="Cadeau10 原声目录",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/opt/moodify/music-media/audio/cadeau10-album1-moodify"),
        help="Moodify 处理后 wav 输出目录",
    )
    parser.add_argument(
        "--manifest-input",
        type=Path,
        default=Path("apps/web/assets/cadeau10-album1.json"),
        help="Cadeau10 原声 manifest",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=Path("apps/web/assets/cadeau10-album1-moodify.json"),
        help="Moodify 处理后公开 manifest sidecar",
    )
    parser.add_argument(
        "--public-base-url",
        type=str,
        default="https://play.rongjingmusic.com/audio/cadeau10-album1-moodify",
        help="公开 URL 模板前缀",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="listen-demo-profile-v1",
        help="Profile 名称",
    )
    parser.add_argument(
        "--check-syntax",
        action="store_true",
        help="只验证 profile 与 manifest 契约,不渲染任何音频",
    )
    args = parser.parse_args()

    profile = LISTEN_DEMO_PROFILE_V1
    if args.check_syntax:
        if not args.manifest_input.exists():
            print(f"ERROR: manifest not found: {args.manifest_input}", file=sys.stderr)
            return 2
        m = json.loads(args.manifest_input.read_text(encoding="utf-8"))
        tracks = m.get("tracks") or []
        if not tracks:
            print("ERROR: manifest has no tracks", file=sys.stderr)
            return 2
        required_keys = {"file", "sha256", "bytes"}
        bad = [t.get("file") for t in tracks if not required_keys.issubset(t.keys())]
        if bad:
            print(f"ERROR: tracks missing keys: {bad}", file=sys.stderr)
            return 2
        expected_keys = set(profile.keys())
        print("OK --check-syntax")
        print(f"  profile name          : listen-demo-profile-v1")
        print(f"  profile params count  : {len(expected_keys)}")
        print(f"  manifest schemaVersion: {m.get('schemaVersion')}")
        print(f"  track count           : {len(tracks)}")
        return 0

    if not args.manifest_input.exists():
        print(f"ERROR: manifest not found: {args.manifest_input}", file=sys.stderr)
        return 2

    manifest = json.loads(args.manifest_input.read_text(encoding="utf-8"))
    tracks = manifest.get("tracks") or []
    if not tracks:
        print("ERROR: manifest has no tracks", file=sys.stderr)
        return 2

    profile = LISTEN_DEMO_PROFILE_V1
    rendered: list[dict] = []
    track_results: list[TrackResult] = []

    for index, track in enumerate(tracks, start=1):
        file_name = track["file"]
        title = track.get("title") or file_name
        source_path = args.input_dir / file_name
        if not source_path.exists():
            print(f"WARN: skip, source not found: {source_path}", file=sys.stderr)
            continue

        output_path = args.output_dir / file_name
        print(f"[{index}/{len(tracks)}] render: {file_name} -> {output_path}", file=sys.stderr)
        stats = render_track(source_path, output_path, profile)
        out_sha = sha256_file(output_path)
        out_bytes = output_path.stat().st_size
        track_results.append(
            TrackResult(
                id=f"track-{index:03d}",
                title=title,
                source_file=file_name,
                source_sha256=track["sha256"],
                source_bytes=int(track["bytes"]),
                output_file=file_name,
                output_sha256=out_sha,
                output_bytes=out_bytes,
                duration_seconds=stats["duration_seconds"],
                public_url=f"{args.public_base_url.rstrip('/')}/{file_name}",
            )
        )
        rendered.append(
            {
                "file": file_name,
                **stats,
            }
        )

    sidecar = {
        "schemaVersion": 1,
        "source": "cadeau10-album1.json",
        "sourceAlbum": manifest.get("album"),
        "profileName": args.profile,
        "processor": {
            "package": "moodify-core-package",
            "module": "moodify.processing.pedalboard_chain",
            "className": "MoodifyDSPChain",
            "method": "process_with_audit",
            "paramsSnapshot": profile,
        },
        "producedAt": datetime.now(timezone.utc).isoformat(),
        "publicBaseUrl": f"{args.public_base_url.rstrip('/')}/",
        "storagePolicy": "Audio binaries are deployment assets and are not committed to Git.",
        "humanListeningReviewRequired": True,
        "tracks": [asdict(t) for t in track_results],
        "renderStats": rendered,
    }

    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote: {args.manifest_output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())