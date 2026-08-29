# File Association Plan

Application-side supported extensions are generated from the importer capability: `.mp3`, `.wav`, `.flac`, `.m4a`, `.aac`, `.ogg`. W09 accepts those Open With arguments.

W12 installer work must register ProgIDs/Open With entries, use quoted executable/`%1` semantics through installer APIs, update registrations on upgrade, and remove only Moodify-owned keys on uninstall. Moodify must not force itself as the default player; Windows/user default-app choice remains authoritative. Multi-file shell invocation behavior must be verified in the packaged build.
