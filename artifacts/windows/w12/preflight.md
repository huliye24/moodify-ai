# W12 Preflight

```text
W11_STATUS = PARTIAL
W12_GATE = PASS
APP_VERSION_REALITY = 0.1.0-beta.1 (package.json authority)
BUILD_TOOLCHAIN = Electron Forge 7 + Vite
PACKAGING_TOOLCHAIN = Squirrel.Windows, per-user
INSTALLER_REALITY = GENERATED, lifecycle not installed/tested
UNINSTALLER_REALITY = Squirrel generated, lifecycle not tested
SIGNING_REALITY = NOT_CONFIGURED / Authenticode NotSigned
UPDATE_REALITY = DISABLED_SAFE_SEAM
DATA_LOCATIONS = Electron userData/moodify/local-state.json
CACHE_LOCATIONS = no Moodify-owned runtime cache
DB_SCHEMA_VERSION = LocalState 6
SETTINGS_SCHEMA_VERSION = 1
RECOVERY_SCHEMA_VERSION = 1
FILE_ASSOCIATION_NEEDS = registration and lifecycle verification outstanding
STARTUP_REGISTRATION_NEEDS = unsupported; setting remains forced OFF
LOGGING_REALITY = structured console + local telemetry/support bundle; no durable crash log
CRASH_DIAGNOSTIC_REALITY = renderer/main markers only; crash-loop protection outstanding
```

W10 remains BLOCKED. W11 human override covered non-cloud settings only.
