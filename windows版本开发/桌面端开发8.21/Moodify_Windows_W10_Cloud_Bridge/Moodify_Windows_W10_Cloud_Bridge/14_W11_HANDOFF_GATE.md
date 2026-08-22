# W11 Handoff Gate — Settings & Audio Environment

W11 会建立用户设置和播放环境管理。

## Required

- [ ] W10 has PASS/PARTIAL with truthful capability report
- [ ] Track/Playback/Queue stable
- [ ] Windows native integration stable
- [ ] Recovery stable
- [ ] cloud config/auth boundary known
- [ ] local/cloud source policy known
- [ ] storage/cache locations known

## W11 Will Build

```text
Output Device
Volume/startup preference
Autoplay policy
Close/tray behavior
Cache policy
Storage location
Cloud preparation preference
Network behavior
Playback preferences
```

## W11 Must Not

- expose Ear/DSP internals
- add giant settings catalog
- override Windows defaults without user intent
- store service secrets
- alter Canon

## Gate

```text
W11_GATE = PASS | BLOCKED
```
