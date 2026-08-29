# Settings Invariants

## S-01 Settings = Preference
Settings 只表达用户偏好，不表达 Track/Queue/Playback 真值。

## S-02 One Authority
禁止 settings.json + localStorage + UI state 三套互相竞争。

## S-03 Unsupported Means Hidden
没有真实能力，不显示假的设置项。

## S-04 Safe Defaults
默认设置必须让应用能直接使用且不会突然出声。

## S-05 Launch ≠ Autoplay
无论开机启动还是普通启动，默认都不自动播放。

## S-06 Device Missing Is Recoverable
输出设备消失不能导致播放器不可用或 crash。

## S-07 Cache ≠ Durable Data
清缓存绝不删除 Library/Playlist/Favorite/History/原始音乐。

## S-08 Storage Migration Is Transactional
切换位置失败必须保留旧位置和旧数据。

## S-09 Cloud Settings Follow Verified Capability
不能设置不存在的 cloud feature。

## S-10 No Secrets
Settings 中不保存 service-key/admin token/provider secret。

## S-11 Reset Settings Is Narrow
恢复默认设置不能变成“恢复出厂并清空数据”。

## S-12 Apply Semantics Explicit
每个设置必须知道何时生效。

## S-13 Close Behavior Is Explicit
Close=Quit 仍是默认；托盘行为必须用户选择。

## S-14 No Advanced Audio Engineering UI
W11 不是 EQ/DSP/ASIO 控制台。

## S-15 No Canon Change
Settings 只是 Windows 产品层。
