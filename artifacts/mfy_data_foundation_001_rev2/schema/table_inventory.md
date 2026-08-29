# Table Inventory — moodify_dev (PolarDB MySQL B) @ 2026-08-13

16 business tables + alembic_version, engine XENGINE, collation utf8mb4_unicode_ci.

| Table | PK | Unique | Indexes | Row count |
|---|---|---|---|---|
| users | id | auth_subject, email | — | 0 |
| creator_profiles | id | user_id, handle | — | 0 |
| tracks | id | — | ix_tracks_creator_status | 0 |
| track_versions | id | uq_track_versions(track_id,version_no) | — | 0 |
| creation_passports | id | — | ix_passports_track | 0 |
| albums | id | — | — | 0 |
| album_tracks | (album_id, track_id) | — | — | 0 |
| follows | id | uq_follows(user_id,creator_id) | ix_follows_creator | 0 |
| favorites | id | uq_favorites(user_id,track_id) | ix_favorites_track | 0 |
| play_events | id | — | ix_play_events_track_created | 0 |
| license_intents | id | — | ix_license_intents_creator_status, ix_license_intents_track | 0 |
| support_intents | id | — | ix_support_intents_creator | 0 |
| cwc_accounts | id | user_id | — | 0 |
| cwc_ledger | id | — | ix_cwc_ledger_account | 0 |
| idempotency_keys | id | uq_idempotency(scope,idempotency_key) | — | 0 |
| audit_events | id | — | ix_audit_events_resource, ix_audit_events_created | 0 |

Row counts from fresh migration (all zero).
