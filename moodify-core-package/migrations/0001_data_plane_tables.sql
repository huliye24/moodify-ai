-- Moodify Data Plane — PolarDB MySQL 8.0 (XEngine) schema (W01-P03)
-- Status: SCHEMA_WRITE_BLOCKED（凭据/授权未满足，未执行）
-- 目标库: moodify_dev（PolarDB pc-bp19502y46246gv6n, 172.27.118.104, VPC 私网）
-- 设计: 非破坏性（CREATE TABLE IF NOT EXISTS；不改动现有 19 表）
-- 规则: INV-03 无大音频 blob；INV-11 幂等注册由应用层保证（UNIQUE 约束辅助）；
--       P04 定义最终 state machine，本文件只建字段承载。

-- 若现有表已存在（moodify_dev 19 表含 tracks/track_versions 等），
-- 需先对照 CURRENT_TO_TARGET_DATA_MAPPING 后再决定合并策略；
-- 本文件默认创建数据平面专属表，避免破坏既有 schema。

CREATE TABLE IF NOT EXISTS tracks (
    track_id VARCHAR(64) PRIMARY KEY,
    owner_scope VARCHAR(128),
    source_object_id VARCHAR(64),
    source_hash CHAR(64) NOT NULL,
    source_format VARCHAR(32),
    source_duration_ms BIGINT,
    source_sample_rate INT,
    source_channels INT,
    status_class VARCHAR(32),
    canonical_source_version VARCHAR(64),
    created_at DATETIME(3) NOT NULL,
    INDEX idx_tracks_hash (source_hash)
) ENGINE = XENGINE;

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(64) PRIMARY KEY,
    track_id VARCHAR(64) NOT NULL,
    job_type VARCHAR(64) NOT NULL,
    requested_at DATETIME(3),
    created_by VARCHAR(64),
    pipeline_version VARCHAR(64),
    processing_profile_version VARCHAR(64),
    current_state VARCHAR(32),
    current_attempt INT DEFAULT 0,
    failure_code VARCHAR(64),
    failure_summary VARCHAR(512),
    started_at DATETIME(3),
    finished_at DATETIME(3),
    ready_object_id VARCHAR(64),
    INDEX idx_jobs_track (track_id),
    CONSTRAINT fk_jobs_track FOREIGN KEY (track_id) REFERENCES tracks(track_id)
) ENGINE = XENGINE;

CREATE TABLE IF NOT EXISTS objects (
    object_id VARCHAR(64) PRIMARY KEY,
    track_id VARCHAR(64) NOT NULL,
    job_id VARCHAR(64),
    artifact_type VARCHAR(32) NOT NULL,
    artifact_role VARCHAR(64),
    bucket VARCHAR(64) NOT NULL,
    object_key VARCHAR(512) NOT NULL,
    content_hash CHAR(64) NOT NULL,
    hash_algorithm VARCHAR(16) NOT NULL DEFAULT 'sha256',
    byte_size BIGINT NOT NULL,
    mime_type VARCHAR(64),
    producer VARCHAR(64) NOT NULL,
    producer_version VARCHAR(64),
    pipeline_version VARCHAR(64),
    parent_object_id VARCHAR(64),
    immutable TINYINT(1) NOT NULL DEFAULT 1,
    retention_class VARCHAR(32) NOT NULL,
    evidence_class VARCHAR(64),
    created_at DATETIME(3) NOT NULL,
    UNIQUE KEY uq_objects_key (object_key),
    INDEX idx_objects_track (track_id),
    INDEX idx_objects_hash (content_hash),
    CONSTRAINT fk_objects_track FOREIGN KEY (track_id) REFERENCES tracks(track_id),
    CONSTRAINT fk_objects_job FOREIGN KEY (job_id) REFERENCES jobs(job_id)
) ENGINE = XENGINE;

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id VARCHAR(64) PRIMARY KEY,
    track_id VARCHAR(64) NOT NULL,
    job_id VARCHAR(64),
    object_id VARCHAR(64),
    evidence_type VARCHAR(64) NOT NULL,
    claim TEXT NOT NULL,
    method VARCHAR(128),
    evaluator VARCHAR(64),
    evaluator_version VARCHAR(64),
    verdict VARCHAR(64),
    uncertainty DOUBLE,
    evidence_object_id VARCHAR(64),
    created_at DATETIME(3) NOT NULL,
    INDEX idx_evidence_track (track_id),
    CONSTRAINT fk_evidence_track FOREIGN KEY (track_id) REFERENCES tracks(track_id),
    CONSTRAINT fk_evidence_job FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    CONSTRAINT fk_evidence_obj FOREIGN KEY (object_id) REFERENCES objects(object_id)
) ENGINE = XENGINE;

CREATE TABLE IF NOT EXISTS versions (
    version_id VARCHAR(64) PRIMARY KEY,
    version_kind VARCHAR(64) NOT NULL,
    version_value VARCHAR(128) NOT NULL,
    created_at DATETIME(3) NOT NULL,
    status VARCHAR(32),
    UNIQUE KEY uq_versions_kind_value (version_kind, version_value)
) ENGINE = XENGINE;
