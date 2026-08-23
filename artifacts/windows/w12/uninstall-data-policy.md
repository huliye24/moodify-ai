# Uninstall Data Policy

Default uninstall removes application binaries and Moodify-owned integrations while preserving durable user data under Electron `userData`. There is no Moodify-owned runtime cache to clear. Original audio remains at user-selected paths and is never in uninstall scope. Squirrel has no custom data-deletion action in this build.
