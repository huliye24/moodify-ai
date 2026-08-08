#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate a Xiaohongshu-ready before/after music processing video.

Inputs:
    before.wav, after.wav, logo.png

Outputs:
    final_video.mp4, cover.png, subtitles.srt, xiaohongshu_caption.txt
"""

from __future__ import annotations

import argparse
import math
import shutil
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1080, 1920
FPS = 30
TOTAL_DURATION = 20.0


@dataclass(frozen=True)
class Scene:
    key: str
    start: float
    end: float
    headline: str
    body: str = ""
    label: str = ""
    audio: str | None = None
    waveform: str | None = None

    @property
    def duration(self) -> float:
        return self.end - self.start


SCENES = [
    Scene(
        key="title",
        start=0,
        end=2,
        headline="AI音乐处理前后对比",
        body="Moodify / 荣景文川音乐工作室",
        label="BEFORE / AFTER",
    ),
    Scene(
        key="before",
        start=2,
        end=8,
        headline="处理前",
        body="人声薄 / 空间平 / 低频散",
        label="BEFORE",
        audio="before",
        waveform="before",
    ),
    Scene(
        key="transition",
        start=8,
        end=10,
        headline="经过荣景文川音乐工作室二次处理",
        body="重新检查频谱、空间、低频与人声质感",
        label="SECOND PROCESSING",
    ),
    Scene(
        key="after",
        start=10,
        end=18,
        headline="处理后",
        body="更清晰 / 更有层次 / 更接近成品",
        label="AFTER",
        audio="after",
        waveform="after",
    ),
    Scene(
        key="cta",
        start=18,
        end=20,
        headline="私信发送30秒音频",
        body="可做初步声音诊断",
        label="MOODIFY",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a 1080x1920 Xiaohongshu before/after music video."
    )
    parser.add_argument("--before", default="before.wav", help="Path to before.wav")
    parser.add_argument("--after", default="after.wav", help="Path to after.wav")
    parser.add_argument("--logo", default="logo.png", help="Path to logo.png")
    parser.add_argument(
        "--out-dir",
        default="outputs/xhs_compare",
        help="Output directory for final_video.mp4 and companion files",
    )
    parser.add_argument("--fps", type=int, default=FPS, help="Video frame rate")
    parser.add_argument("--bitrate", default="8000k", help="Video bitrate")
    return parser.parse_args()


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for item in candidates:
        if item and Path(item).exists():
            return ImageFont.truetype(item, size=size)
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_center_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    spacing: int = 18,
) -> None:
    x, y = xy
    lines = text.splitlines()
    heights = [text_size(draw, line, font)[1] for line in lines]
    total_h = sum(heights) + spacing * (len(lines) - 1)
    cursor = y - total_h // 2
    for line, line_h in zip(lines, heights):
        line_w, _ = text_size(draw, line, font)
        draw.text((x - line_w // 2, cursor), line, font=font, fill=fill)
        cursor += line_h + spacing


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int] | None = None,
    radius: int = 8,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def vertical_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / max(1, H - 1)
        arr[y, :, :] = [
            int(top[i] * (1 - t) + bottom[i] * t)
            for i in range(3)
        ]
    return Image.fromarray(arr, "RGB")


def add_soft_light(base: Image.Image, accent: tuple[int, int, int], center: tuple[int, int], radius: int) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = overlay.load()
    cx, cy = center
    for y in range(max(0, cy - radius), min(H, cy + radius)):
        for x in range(max(0, cx - radius), min(W, cx + radius)):
            d = math.hypot(x - cx, y - cy) / radius
            if d < 1:
                a = int((1 - d) ** 2 * 95)
                px[x, y] = (*accent, a)
    base.alpha_composite(overlay)


def wav_to_float_array(path: Path, max_seconds: float = 30.0) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()
        frame_count = min(wf.getnframes(), int(frame_rate * max_seconds))
        raw = wf.readframes(frame_count)

    if sample_width == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif sample_width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    elif sample_width == 3:
        byte_data = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        signed = (
            byte_data[:, 0].astype(np.int32)
            | (byte_data[:, 1].astype(np.int32) << 8)
            | (byte_data[:, 2].astype(np.int32) << 16)
        )
        signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
        data = signed.astype(np.float32) / 8388608
    elif sample_width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648
    else:
        raise ValueError(f"Unsupported WAV sample width: {sample_width}")

    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    if data.size == 0:
        return np.zeros(1024, dtype=np.float32)
    return np.nan_to_num(data)


def waveform_points(path: Path, width: int = 860) -> np.ndarray:
    samples = wav_to_float_array(path)
    samples = samples / max(1e-6, float(np.max(np.abs(samples))))
    bucket_count = max(64, width)
    bucket_size = max(1, samples.size // bucket_count)
    trimmed = samples[: bucket_size * bucket_count]
    if trimmed.size == 0:
        return np.zeros(bucket_count, dtype=np.float32)
    buckets = trimmed.reshape(bucket_count, bucket_size)
    peaks = np.max(np.abs(buckets), axis=1)
    return peaks.astype(np.float32)


def draw_waveform(
    draw: ImageDraw.ImageDraw,
    points: np.ndarray,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    muted: bool = False,
) -> None:
    left, top, right, bottom = box
    mid = (top + bottom) // 2
    height = bottom - top
    count = len(points)
    step = (right - left) / max(1, count - 1)
    for i, amp in enumerate(points):
        x = int(left + i * step)
        bar_h = int(amp * height * (0.48 if not muted else 0.34))
        alpha = 190 if not muted else 115
        draw.line((x, mid - bar_h, x, mid + bar_h), fill=(*color, alpha), width=2)

    draw.line((left, mid, right, mid), fill=(255, 255, 255, 60), width=2)


def paste_logo(base: Image.Image, logo_path: Path) -> None:
    if not logo_path.exists():
        return
    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception:
        return

    max_w, max_h = 220, 180
    logo.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    x = W - logo.width - 70
    y = 58
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 120)).filter(ImageFilter.GaussianBlur(12))
    base.alpha_composite(shadow, (x + 2, y + 5))
    base.alpha_composite(logo, (x, y))


def make_scene_image(
    scene: Scene,
    out_path: Path,
    logo_path: Path,
    before_points: np.ndarray,
    after_points: np.ndarray,
) -> None:
    base = vertical_gradient((15, 18, 27), (29, 34, 48)).convert("RGBA")
    add_soft_light(base, (44, 183, 186), (180, 620), 520)
    add_soft_light(base, (220, 176, 96), (930, 1320), 520)
    draw = ImageDraw.Draw(base, "RGBA")

    title_font = find_font(86, bold=True)
    headline_font = find_font(76, bold=True)
    body_font = find_font(46)
    label_font = find_font(30, bold=True)
    small_font = find_font(30)

    draw.text((70, 64), "Moodify", font=find_font(40, bold=True), fill=(248, 250, 252, 235))
    draw.text((70, 116), "荣景文川音乐工作室", font=small_font, fill=(203, 213, 225, 210))
    paste_logo(base, logo_path)

    rounded_box(
        draw,
        (70, 250, 1010, 1560),
        fill=(7, 10, 18, 110),
        outline=(255, 255, 255, 40),
        radius=8,
        width=2,
    )

    if scene.waveform == "before":
        draw_waveform(draw, before_points, (120, 650, 980, 1120), (84, 201, 202), muted=False)
    elif scene.waveform == "after":
        draw_waveform(draw, after_points, (120, 650, 980, 1120), (242, 188, 92), muted=False)
    else:
        draw_waveform(draw, before_points, (120, 670, 980, 960), (84, 201, 202), muted=True)
        draw_waveform(draw, after_points, (120, 960, 980, 1250), (242, 188, 92), muted=True)

    label_color = (84, 201, 202, 230) if scene.key == "before" else (242, 188, 92, 230)
    if scene.key in {"title", "transition", "cta"}:
        label_color = (255, 255, 255, 190)

    label_w, label_h = text_size(draw, scene.label, label_font)
    rounded_box(
        draw,
        (W // 2 - label_w // 2 - 30, 346, W // 2 + label_w // 2 + 30, 346 + label_h + 26),
        fill=(255, 255, 255, 24),
        outline=label_color,
        radius=8,
        width=2,
    )
    draw.text((W // 2 - label_w // 2, 358), scene.label, font=label_font, fill=label_color)

    if scene.key == "title":
        draw_center_text(draw, (W // 2, 785), scene.headline, title_font, (255, 255, 255, 245))
        draw_center_text(draw, (W // 2, 930), scene.body, body_font, (226, 232, 240, 220))
    elif scene.key == "transition":
        draw_center_text(draw, (W // 2, 800), scene.headline, headline_font, (255, 255, 255, 245), spacing=22)
        draw_center_text(draw, (W // 2, 950), scene.body, body_font, (226, 232, 240, 215), spacing=18)
    elif scene.key == "cta":
        draw_center_text(draw, (W // 2, 770), scene.headline, headline_font, (255, 255, 255, 245), spacing=20)
        draw_center_text(draw, (W // 2, 920), scene.body, body_font, (242, 188, 92, 235), spacing=18)
    else:
        draw_center_text(draw, (W // 2, 510), scene.headline, headline_font, (255, 255, 255, 245))
        draw_center_text(draw, (W // 2, 1295), scene.body, body_font, (226, 232, 240, 230))

    draw.text((70, 1648), "AI音乐二次处理 / Before & After", font=small_font, fill=(203, 213, 225, 190))
    draw.text((70, 1700), "私信发送30秒音频，可做初步声音诊断", font=small_font, fill=(248, 250, 252, 220))
    draw.line((70, 1604, 1010, 1604), fill=(255, 255, 255, 42), width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_path, quality=95)


def srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hh = millis // 3_600_000
    millis %= 3_600_000
    mm = millis // 60_000
    millis %= 60_000
    ss = millis // 1000
    ms = millis % 1000
    return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"


def write_srt(path: Path) -> None:
    subtitle_lines = []
    for idx, scene in enumerate(SCENES, start=1):
        text = scene.headline if not scene.body else f"{scene.headline}：{scene.body}"
        subtitle_lines.append(
            f"{idx}\n{srt_time(scene.start)} --> {srt_time(scene.end)}\n{text}\n"
        )
    path.write_text("\n".join(subtitle_lines), encoding="utf-8")


def write_caption(path: Path) -> None:
    caption = """AI音乐处理前后对比。

很多AI生成音乐不是不能用，而是还需要二次处理：
人声质感、空间层次、低频稳定度、整体成品感，都需要重新校准。

Moodify / 荣景文川音乐工作室
可做 AI 音乐声音诊断、混音方向建议、二次处理参考。

私信发送30秒音频，可做初步声音诊断。

#AI音乐 #音乐后期 #混音 #母带 #声音诊断 #小红书音乐人 #AI音乐处理 #Moodify #荣景文川音乐工作室
"""
    path.write_text(caption, encoding="utf-8")


def clip_with_duration(clip, duration: float):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(duration)
    return clip.set_duration(duration)


def clip_with_audio(clip, audio):
    if hasattr(clip, "with_audio"):
        return clip.with_audio(audio)
    return clip.set_audio(audio)


def clip_with_start(clip, start: float):
    if hasattr(clip, "with_start"):
        return clip.with_start(start)
    return clip.set_start(start)


def audio_subclip(clip, start: float, end: float):
    if hasattr(clip, "subclipped"):
        return clip.subclipped(start, end)
    return clip.subclip(start, end)


def build_video(
    scene_paths: Iterable[Path],
    before_path: Path,
    after_path: Path,
    out_path: Path,
    fps: int,
    bitrate: str,
) -> None:
    try:
        from moviepy import AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips
    except ImportError:
        try:
            from moviepy.editor import AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips
        except ImportError as exc:
            raise RuntimeError(
                "MoviePy is required to render final_video.mp4. "
                "Install dependencies with: pip install -r tools/xhs_compare_video/requirements.txt"
            ) from exc

    video_clips = [
        clip_with_duration(ImageClip(str(path)), scene.duration)
        for path, scene in zip(scene_paths, SCENES)
    ]
    video = concatenate_videoclips(video_clips, method="compose")

    audio_parts = []
    before_audio = AudioFileClip(str(before_path))
    after_audio = AudioFileClip(str(after_path))
    before_end = min(6.0, float(before_audio.duration or 6.0))
    after_end = min(8.0, float(after_audio.duration or 8.0))
    audio_parts.append(clip_with_start(audio_subclip(before_audio, 0, before_end), 2.0))
    audio_parts.append(clip_with_start(audio_subclip(after_audio, 0, after_end), 10.0))

    composite_audio = clip_with_duration(CompositeAudioClip(audio_parts), TOTAL_DURATION)
    video = clip_with_audio(clip_with_duration(video, TOTAL_DURATION), composite_audio)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(out_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        bitrate=bitrate,
        preset="medium",
        threads=4,
    )

    video.close()
    before_audio.close()
    after_audio.close()
    for clip in video_clips:
        clip.close()


def main() -> None:
    args = parse_args()
    before_path = Path(args.before).resolve()
    after_path = Path(args.after).resolve()
    logo_path = Path(args.logo).resolve()
    out_dir = Path(args.out_dir).resolve()
    frame_dir = out_dir / "frames"

    for required in [before_path, after_path, logo_path]:
        if not required.exists():
            raise FileNotFoundError(f"Missing input file: {required}")

    before_points = waveform_points(before_path)
    after_points = waveform_points(after_path)

    scene_paths = []
    for scene in SCENES:
        scene_path = frame_dir / f"{scene.key}.png"
        make_scene_image(scene, scene_path, logo_path, before_points, after_points)
        scene_paths.append(scene_path)

    shutil.copyfile(scene_paths[0], out_dir / "cover.png")
    write_srt(out_dir / "subtitles.srt")
    write_caption(out_dir / "xiaohongshu_caption.txt")
    build_video(
        scene_paths=scene_paths,
        before_path=before_path,
        after_path=after_path,
        out_path=out_dir / "final_video.mp4",
        fps=args.fps,
        bitrate=args.bitrate,
    )

    print(f"Done. Outputs written to: {out_dir}")
    print(" - final_video.mp4")
    print(" - cover.png")
    print(" - subtitles.srt")
    print(" - xiaohongshu_caption.txt")


if __name__ == "__main__":
    main()
