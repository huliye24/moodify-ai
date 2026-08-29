# Installer Contract

Squirrel.Windows creates a per-user installer and uninstall entry without requiring machine-wide privileges. It may create Moodify shortcuts. It must preserve `%APPDATA%/Moodify/moodify`, never touch source audio, never force startup, and never seize default-player ownership.

Installer generated successfully. Actual clean install, association registration and lifecycle cleanup are not yet verified; therefore `INSTALLER = PARTIAL`.
