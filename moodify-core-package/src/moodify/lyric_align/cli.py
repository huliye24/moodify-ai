from __future__ import annotations

import argparse
import json
import sys

from moodify.lyric_align.lyrics import clean_lyrics_file
from moodify.lyric_align.pipeline import run_alignment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moodify-lyrics")
    sub = parser.add_subparsers(dest="command", required=True)

    clean = sub.add_parser("clean", help="Remove non-lyric structural labels.")
    clean.add_argument("--lyrics", required=True)

    align = sub.add_parser("align", help="Align authoritative lyrics to final audio.")
    align.add_argument("--audio", required=True)
    align.add_argument("--lyrics", required=True)
    align.add_argument("--translation-lyrics")
    align.add_argument("--language", required=True)
    align.add_argument("--backend", choices=["heuristic", "whisperx"], default="heuristic")
    align.add_argument("--separate-vocals", choices=["never", "auto", "always"], default="auto")
    align.add_argument("--device", default="cpu")
    align.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "clean":
            print("\n".join(clean_lyrics_file(args.lyrics)))
            return 0
        if args.command == "align":
            manifest = run_alignment(
                audio_path=args.audio,
                lyrics_path=args.lyrics,
                translation_path=args.translation_lyrics,
                output_dir=args.output,
                language=args.language,
                backend_name=args.backend,
                separate_vocals=args.separate_vocals,
                device=args.device,
            )
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
