# Known Issues

## P0 BLOCKER

None identified.

## P1 MUST FIX BEFORE BETA

- Clean-machine install/launch/import/play/uninstall is unverified.
- Previous-Alpha installer upgrade and durable-data comparison are unverified.
- Uninstall/reinstall preservation and integration cleanup are unverified.
- File associations are not registered/tested through install lifecycle.
- Durable local crash artifact and crash-loop protection are absent.
- Required performance baselines and playback soak are not run.

## P2 ACCEPTED BETA LIMITATIONS

- Installer is unsigned and may trigger Windows trust warnings.
- Cloud preparation is unavailable; published catalogue playback only.
- Startup registration remains unsupported and OFF.
- Packaged output-device/hotplug hardware verification is pending.

## P3 FOLLOW-UP

- Add stable Git commit/build-number injection when implementation receives Git metadata.
