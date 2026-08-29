# Index Inventory — moodify_dev

| Table | Index | Columns |
|---|---|---|
| tracks | ix_tracks_creator_status | (creator_id, status) |
| creation_passports | ix_passports_track | (track_id) |
| follows | ix_follows_creator | (creator_id) |
| favorites | ix_favorites_track | (track_id) |
| play_events | ix_play_events_track_created | (track_id, created_at) |
| license_intents | ix_license_intents_creator_status | (creator_id, status) |
| license_intents | ix_license_intents_track | (track_id) |
| support_intents | ix_support_intents_creator | (creator_id) |
| cwc_ledger | ix_cwc_ledger_account | (account_id) |
| audit_events | ix_audit_events_resource | (resource_type, resource_id) |
| audit_events | ix_audit_events_created | (created_at) |

Unique indexes: users(auth_subject), users(email), creator_profiles(user_id),
creator_profiles(handle), track_versions(track_id, version_no),
follows(user_id, creator_id), favorites(user_id, track_id),
idempotency_keys(scope, idempotency_key), cwc_accounts(user_id).
