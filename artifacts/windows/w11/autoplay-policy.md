# Autoplay / Volume Policy

App launch and W08 recovery remain silent; `autoplay_policy` is fixed to `OFF_ON_APP_LAUNCH` and is shown as explanatory state, not a dangerous toggle. W09 explicit Open With remains an explicit user action and continues to play. W10 has no READY event and cannot trigger audio.

`restore_volume=true` applies W08's clamped saved volume. When false, next launch uses safe 80%, not 100%. Changing this preference does not disrupt the current session.
