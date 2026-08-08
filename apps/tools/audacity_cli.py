"""Audacity mod-script-pipe bridge — drive import/select/effect/export via named pipes.

Requires Audacity running with the mod-script-pipe module enabled
(Edit -> Preferences -> Modules -> mod-script-pipe -> Enabled, then restart).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TextIO


TO_AUDACITY_PIPE = r"\\.\pipe\ToSrvPipe"
FROM_AUDACITY_PIPE = r"\\.\pipe\FromSrvPipe"
COMMAND_END = "\r\n\0"


class AudacityClient:
    def __init__(self) -> None:
        self.writer: TextIO | None = None
        self.reader: TextIO | None = None

    def connect(self) -> None:
        try:
            self.writer = open(TO_AUDACITY_PIPE, mode="w", newline="", encoding="utf-8")
            self.reader = open(
                FROM_AUDACITY_PIPE, mode="r", newline="",
                encoding="utf-8", errors="replace",
            )
        except OSError as exc:
            raise RuntimeError(
                "无法连接 Audacity。请确认：\n"
                "1. Audacity 已启动；\n"
                "2. mod-script-pipe 已启用（编辑→首选项→模块）；\n"
                "3. 启用模块后已经重启 Audacity。"
            ) from exc

    def command(self, command: str) -> str:
        if self.writer is None or self.reader is None:
            raise RuntimeError("尚未连接 Audacity。")
        print(f"> {command}")
        self.writer.write(command + COMMAND_END)
        self.writer.flush()
        response_lines: list[str] = []
        while True:
            line = self.reader.readline()
            if line == "":
                raise RuntimeError("Audacity 管道已断开。")
            if line == "\n":
                break
            response_lines.append(line)
        response = "".join(response_lines).strip()
        print(response or "(empty response)")
        return response

    def close(self) -> None:
        if self.writer is not None:
            self.writer.close()
        if self.reader is not None:
            self.reader.close()


def audacity_path(path: Path) -> str:
    return path.resolve().as_posix()


def process_audio(source: Path, destination: Path, commands: list[str]) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"输入文件不存在：{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    client = AudacityClient()
    try:
        client.connect()
        client.command(f'Import2: Filename="{audacity_path(source)}"')
        client.command("SelectAll:")
        for cmd in commands:
            client.command(cmd)
        client.command(f'Export2: Filename="{audacity_path(destination)}" NumChannels=2')
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="通过 mod-script-pipe 控制 Audacity。")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--commands",
        nargs="+",
        default=[],
        help="Audacity 脚本命令，例如 'Normalize: PeakLevel=-1'",
    )
    parser.add_argument(
        "--pipe-check",
        action="store_true",
        help="只检查命名管道是否存在，不执行处理",
    )
    args = parser.parse_args()

    if args.pipe_check:
        import os
        to_ok = os.path.exists(TO_AUDACITY_PIPE)
        from_ok = os.path.exists(FROM_AUDACITY_PIPE)
        print(f"ToSrvPipe:   {'存在' if to_ok else '不存在'}")
        print(f"FromSrvPipe: {'存在' if from_ok else '不存在'}")
        if not (to_ok and from_ok):
            print("请启动 Audacity 并启用 mod-script-pipe 模块后重试。")
            return 1
        return 0

    try:
        process_audio(args.input, args.output, args.commands)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    print(f"处理完成：{args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
