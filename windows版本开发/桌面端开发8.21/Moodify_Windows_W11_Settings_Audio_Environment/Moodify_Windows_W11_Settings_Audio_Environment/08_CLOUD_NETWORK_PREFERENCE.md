# Cloud & Network Preference Policy

## Capability Gate

只暴露 W10 已真实验证的 cloud 能力。

## Preparation Trigger

W11 默认：

```text
MANUAL
```

只有真实产品决策明确后才允许：
```text
AUTO_ON_IMPORT
AUTO_ON_FIRST_PLAY
```

## Local Fallback

推荐：

```text
fallback_to_local = true
```

云端失败时，用户仍能听本地版本。

## Network

Windows 桌面端只暴露实际有意义且可检测的网络策略。

若 runtime 能识别 metered connection，可以考虑：

```text
Allow cloud preparation on metered networks
```

如果不能识别：
不要显示“仅 Wi-Fi”。

## Background Refresh

active preparation 状态刷新可以后台进行，但必须服从 W10 backoff，不能因设置页引入高频 polling。
