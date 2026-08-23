# W11 UI Settings Contract

```text
VISUAL_REDESIGN = FORBIDDEN
```

## Structure

一个简洁 secondary page：

```text
设置

播放
应用
存储
Moodify Cloud
```

只显示 build 中真实支持的能力。

## Progressive Disclosure

```text
unsupported → hide
```

不要用一堆 disabled “Coming Soon”。

## Playback

可能显示：
- 输出设备
- 恢复上次音量
- 启动时自动播放（默认关闭，甚至可不暴露）

## App

可能显示：
- 关闭窗口时
- 开机启动

## Storage

可能显示：
- 缓存占用
- 清理缓存
- 缓存位置

## Cloud

可能显示：
- 云端准备方式
- 网络相关真实设置

## Never Show

- API endpoint
- service-key
- provider selector
- Ear
- Stem
- DSP
- Evidence
- worker count
- model settings
