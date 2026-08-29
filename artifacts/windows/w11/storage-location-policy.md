# Storage Location Policy

Core JSON state remains below Electron `userData/moodify`; original user music remains at its imported path and is never moved. App-data relocation is deferred because no transactional migration/rollback implementation exists. Cache location is hidden because no runtime cache exists.

Future cache relocation must validate writable target, copy, verify, switch authority and clean old cache only after success. Core data relocation requires separate migration authority and must not be improvised in Settings.
