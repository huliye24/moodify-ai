"""Run a reproducible Audacity post-processing stage through mod-script-pipe."""

from __future__ import annotations

import argparse
from pathlib import Path


TO_PIPE = r"\\.\pipe\ToSrvPipe"
FROM_PIPE = r"\\.\pipe\FromSrvPipe"
EOL = "\r\n\0"


class AudacityPipe:
    def __init__(self) -> None:
        self.to_file = open(TO_PIPE, "w", encoding="utf-8")
        self.from_file = open(FROM_PIPE, "rt", encoding="utf-8", errors="replace")

    def command(self, text: str) -> str:
        self.to_file.write(text + EOL)
        self.to_file.flush()
        lines: list[str] = []
        while True:
            line = self.from_file.readline()
            if not line:
                raise RuntimeError(f"Audacity pipe closed while running: {text}")
            if line.startswith("BatchCommand finished:"):
                lines.append(line.strip())
                break
            if line.strip():
                lines.append(line.strip())
        response = "\n".join(lines)
        if "BatchCommand finished: OK" not in response:
            raise RuntimeError(f"Audacity command failed: {text}\n{response}")
        print(f"{text}\n  {response}")
        return response


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("project", type=Path)
    parser.add_argument("--duration", type=float, default=179.84)
    parser.add_argument("--gentle", action="store_true", help="Use transparent platform-mastering settings")
    parser.add_argument("--macro", default="", help="Apply a named Audacity macro instead of the built-in chain")
    parser.add_argument("--netease", action="store_true", help="Transparent final delivery pass for streaming")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.project.parent.mkdir(parents=True, exist_ok=True)

    # Audacity's scripting parser is more reliable with forward-slash paths on
    # Windows, especially when the filename contains spaces or non-ASCII text.
    input_path = args.input.resolve().as_posix()
    output_path = args.output.resolve().as_posix()
    project_path = args.project.resolve().as_posix()

    client = AudacityPipe()
    client.command("New:")
    client.command(f'Import2: Filename="{input_path}"')
    client.command("SetProject: Rate=48000")
    client.command(
        f"Select: Start=0 End={args.duration:.3f} "
        "RelativeTo=ProjectStart Track=0 TrackCount=1 Mode=Set"
    )
    if args.netease:
        client.command('Normalize: ApplyVolume="0" RemoveDcOffset="1" StereoIndependent="0"')
        client.command("Select: Start=0 End=0.05 RelativeTo=ProjectStart Track=0 TrackCount=1 Mode=Set")
        client.command('FadeIn: Use_Preset="<Current Settings>"')
        client.command("Select: Start=0 End=0.10 RelativeTo=ProjectEnd Track=0 TrackCount=1 Mode=Set")
        client.command('FadeOut: Use_Preset="<Current Settings>"')
        client.command(
            f"Select: Start=0 End={args.duration:.3f} "
            "RelativeTo=ProjectStart Track=0 TrackCount=1 Mode=Set"
        )
        client.command(
            "LoudnessNormalization: StereoIndependent=False LUFSLevel=-14.0 "
            "DualMono=False NormalizeTo=0"
        )
        client.command(
            "Limiter: thresholdDb=-1.8 makeupTargetDb=-1.2 kneeWidthDb=1 "
            "lookaheadMs=2 releaseMs=40"
        )
    elif args.macro:
        client.command(f"Macro_{args.macro}:")
    elif args.gentle:
        client.command(
            "LoudnessNormalization: StereoIndependent=False LUFSLevel=-13.8 "
            "DualMono=False NormalizeTo=0"
        )
        client.command(
            "Limiter: thresholdDb=-1.8 makeupTargetDb=-1.2 kneeWidthDb=1 "
            "lookaheadMs=2 releaseMs=40"
        )
    else:
        client.command("BassAndTreble: Bass=-0.5 Treble=0.8 Gain=0")
        client.command(
            "Compressor: thresholdDb=-16 makeupGainDb=0 kneeWidthDb=6 "
            "compressionRatio=1.2 lookaheadMs=1 attackMs=30 releaseMs=180"
        )
        client.command(
            "LoudnessNormalization: StereoIndependent=False LUFSLevel=-11.6 "
            "DualMono=False NormalizeTo=0"
        )
        client.command(
            "Limiter: thresholdDb=-2.5 makeupTargetDb=-1.4 kneeWidthDb=2 "
            "lookaheadMs=2 releaseMs=30"
        )
    client.command(f'Export2: Filename="{output_path}" NumChannels=2')
    client.command(f'SaveProject2: Filename="{project_path}" AddToHistory=False')


if __name__ == "__main__":
    main()
