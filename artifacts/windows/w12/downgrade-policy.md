# Downgrade Policy

`UNSUPPORTED_BUT_SAFE`. A newer schema is sanitized while recognized durable collections are preserved and transient playback/recovery is ignored. Older binaries do not have a proven future-schema refusal mechanism; users must restore the automatic pre-migration backup before downgrading. Installed downgrade testing remains outstanding.
