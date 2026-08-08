# Moodify 小红书前后对比视频生成器

这个工具用于 Moodify / 荣景文川音乐工作室的 AI 音乐二次处理展示。

输入：

- `before.wav`
- `after.wav`
- `logo.png`

输出：

- `final_video.mp4`：1080x1920、约 20 秒、小红书竖屏视频
- `cover.png`：封面图
- `subtitles.srt`：字幕文件
- `xiaohongshu_caption.txt`：小红书发布文案

## 视频结构

- 0-2 秒：标题 `AI音乐处理前后对比`
- 2-8 秒：播放 `before.wav` 片段，显示 `处理前：人声薄 / 空间平 / 低频散`
- 8-10 秒：显示 `经过荣景文川音乐工作室二次处理`
- 10-18 秒：播放 `after.wav` 片段，显示 `处理后：更清晰 / 更有层次 / 更接近成品`
- 18-20 秒：显示 CTA `私信发送30秒音频，可做初步声音诊断`

脚本会自动从 `before.wav` 和 `after.wav` 生成波形背景视觉。

## 安装依赖

建议在项目根目录创建虚拟环境：

```bash
python -m venv .venv-video
.venv-video\Scripts\activate
pip install -r tools\xhs_compare_video\requirements.txt
```

如果你使用 macOS / Linux：

```bash
python -m venv .venv-video
source .venv-video/bin/activate
pip install -r tools/xhs_compare_video/requirements.txt
```

## 运行

把素材放在项目根目录，文件名使用默认值：

```bash
python tools\xhs_compare_video\generate_xhs_compare_video.py
```

或显式指定输入与输出目录：

```bash
python tools\xhs_compare_video\generate_xhs_compare_video.py ^
  --before before.wav ^
  --after after.wav ^
  --logo logo.png ^
  --out-dir outputs\xhs_compare
```

输出会生成在：

```text
outputs/xhs_compare/
```

## 参数

```bash
python tools\xhs_compare_video\generate_xhs_compare_video.py --help
```

常用参数：

- `--before`：处理前音频路径，默认 `before.wav`
- `--after`：处理后音频路径，默认 `after.wav`
- `--logo`：Logo 图片路径，默认 `logo.png`
- `--out-dir`：输出目录，默认 `outputs/xhs_compare`
- `--fps`：帧率，默认 `30`
- `--bitrate`：视频码率，默认 `8000k`

## 注意事项

- `before.wav` 至少建议 6 秒，`after.wav` 至少建议 8 秒。
- 如果音频较短，脚本会按实际长度播放，剩余片段保持静音。
- 中文字体会优先使用 Windows 的微软雅黑；在其他系统上会尝试使用常见中文字体或 Noto 字体。
- MoviePy 会调用 FFmpeg。正常情况下依赖会通过 `imageio-ffmpeg` 自动提供 FFmpeg。
