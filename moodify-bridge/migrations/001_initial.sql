CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS ledger_seq START 1;
CREATE TABLE IF NOT EXISTS ledger_events (
    sequence BIGINT PRIMARY KEY DEFAULT nextval('ledger_seq'),
    event_id UUID UNIQUE NOT NULL,
    aggregate_type VARCHAR NOT NULL,
    aggregate_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    schema_version VARCHAR NOT NULL,
    payload_json JSON NOT NULL,
    payload_sha256 VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS cases (
    case_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    title VARCHAR NOT NULL,
    moodify_version VARCHAR NOT NULL,
    golden BOOLEAN NOT NULL,
    payload_json JSON NOT NULL,
    payload_sha256 VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id UUID PRIMARY KEY,
    case_id UUID NOT NULL,
    asset_id UUID,
    adapter VARCHAR NOT NULL,
    measured_at TIMESTAMPTZ NOT NULL,
    parquet_path VARCHAR,
    payload_json JSON NOT NULL,
    payload_sha256 VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id UUID PRIMARY KEY,
    rule_id VARCHAR NOT NULL,
    rule_version VARCHAR NOT NULL,
    approver VARCHAR NOT NULL,
    approved_at TIMESTAMPTZ NOT NULL,
    payload_json JSON NOT NULL,
    payload_sha256 VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS validations (
    validation_id UUID PRIMARY KEY,
    subject_type VARCHAR NOT NULL,
    subject_id VARCHAR NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL,
    valid BOOLEAN NOT NULL,
    payload_json JSON NOT NULL
);

