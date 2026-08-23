# Metadata Fallback Policy

- title: trimmed embedded title -> filename stem -> `未知歌曲`
- artist: trimmed embedded artist -> `未知艺术家`
- album: trimmed embedded album -> `未知专辑`
- duration: invalid, zero or unknown -> `--:--`
- availability: unavailable rows remain visible but cannot play
- long values: ellipsis plus title tooltip
- Unicode: string operations preserve Chinese/Japanese/Korean/accented Latin/emoji
