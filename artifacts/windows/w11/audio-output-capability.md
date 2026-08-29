# Audio Output Capability

```text
ENUMERATE_OUTPUTS = SUPPORTED (navigator.mediaDevices.enumerateDevices)
SELECT_OUTPUT = SUPPORTED (HTMLMediaElement.setSinkId)
HOTPLUG_EVENTS = SUPPORTED (devicechange)
PERSIST_DEVICE_ID = SUPPORTED (validated Settings string)
DEFAULT_DEVICE_FOLLOW = SUPPORTED (empty sink/System Default)
```

The selector is rendered only when `setSinkId` exists in the actual Chromium build. Labels may remain generic until OS media permission exposes them. No ASIO/exclusive/engineering controls are claimed.
