"""MIDI → MusicXML（Moodify Studio 曲谱工作台 · music21, MIT）。

用法: python midi_to_musicxml.py <input.mid> <output.musicxml>
"""
import sys

from music21 import converter


def main():
    if len(sys.argv) != 3:
        print("usage: midi_to_musicxml.py <input.mid> <output.musicxml>", file=sys.stderr)
        sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    score = converter.parse(src)
    # 量化到 1/16 与 1/8 三连音，MIDI 转谱最常用的可读粒度
    score = score.makeNotation(inPlace=False)
    score.write("musicxml", fp=dst)
    print(f"musicxml: {dst}", flush=True)
    print('{"ok": true}', flush=True)


if __name__ == "__main__":
    main()
