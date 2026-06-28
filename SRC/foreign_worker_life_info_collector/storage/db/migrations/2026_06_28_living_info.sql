-- WorkConnect living_info first physical schema draft.
-- Purpose:
--   Preserve living-domain source evidence, normalized meaning, demand signals,
--   and topic clusters before anything becomes a content candidate.
--
-- Ownership boundary:
--   living_info.source_item is source/domain evidence, not publishable content.
--   living_info.source_signal is demand signal only and must not be treated as fact.
--   living_info.topic_cluster is the first living-domain object that may later
--   produce content.content_candidate after review gates are implemented.
--   Final review/publish ownership remains in content.content_candidate.
--   Community/trend signals must not directly create public content.
--
-- This migration is additive only.
-- It intentionally does not create fact_point or card_point tables.
-- It intentionally does not add triggers, stored procedures, jobs, seed rows,
-- backfill rows, or changes to existing schemas.

CREATE SCHEMA IF NOT EXISTS living_info;

CREATE TABLE IF NOT EXISTS living_info.source_item (
    id BIGSERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    canonical_url TEXT NOT NULL DEFAULT '',
    publishable_link_url TEXT NOT NULL DEFAULT '',
    source_name VARCHAR(200) NOT NULL DEFAULT '',
    source_type VARCHAR(60) NOT NULL,
    source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_PAGE',
    language VARCHAR(20) NOT NULL DEFAULT 'en',
    country VARCHAR(80) NOT NULL DEFAULT 'Korea',
    region_in_korea VARCHAR(120) NOT NULL DEFAULT '',
    raw_title TEXT NOT NULL DEFAULT '',
    raw_summary TEXT NOT NULL DEFAULT '',
    raw_body TEXT NOT NULL DEFAULT '',
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMPTZ,
    source_trust_level VARCHAR(40) NOT NULL DEFAULT 'DISCOVERY',
    privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'LOW',
    duplicate_key VARCHAR(160) NOT NULL,
    content_hash VARCHAR(160) NOT NULL DEFAULT '',
    source_status VARCHAR(40) NOT NULL DEFAULT 'COLLECTED',
    active_yn CHAR(1) NOT NULL DEFAULT 'Y',
    raw_ref_table VARCHAR(120) NOT NULL DEFAULT '',
    raw_ref_id BIGINT,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ux_living_source_item_duplicate_key UNIQUE(duplicate_key),
    CONSTRAINT ck_living_source_item_active_yn CHECK (active_yn IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_living_source_item_type_collected
ON living_info.source_item(source_type, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_living_source_item_trust_collected
ON living_info.source_item(source_trust_level, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_living_source_item_status_collected
ON living_info.source_item(source_status, collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_living_source_item_canonical_url
ON living_info.source_item(canonical_url);

CREATE INDEX IF NOT EXISTS idx_living_source_item_content_hash
ON living_info.source_item(content_hash);

CREATE INDEX IF NOT EXISTS idx_living_source_item_raw_ref
ON living_info.source_item(raw_ref_table, raw_ref_id);

CREATE TABLE IF NOT EXISTS living_info.normalized_item (
    id BIGSERIAL PRIMARY KEY,
    source_item_id BIGINT NOT NULL REFERENCES living_info.source_item(id),
    normalized_primary_category VARCHAR(60) NOT NULL,
    normalized_secondary_category VARCHAR(120) NOT NULL DEFAULT '',
    source_usage VARCHAR(60) NOT NULL,
    info_signal_type VARCHAR(60) NOT NULL,
    target_user VARCHAR(120) NOT NULL DEFAULT '',
    action_type VARCHAR(120) NOT NULL DEFAULT '',
    topic_key_candidate VARCHAR(180) NOT NULL DEFAULT '',
    validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y',
    validation_source_type VARCHAR(60) NOT NULL DEFAULT '',
    actionability_score NUMERIC(8,4) NOT NULL DEFAULT 0,
    repeatability_score NUMERIC(8,4) NOT NULL DEFAULT 0,
    source_reliability_score NUMERIC(8,4) NOT NULL DEFAULT 0,
    normalization_confidence NUMERIC(8,4) NOT NULL DEFAULT 0,
    normalization_reason TEXT NOT NULL DEFAULT '',
    status VARCHAR(40) NOT NULL DEFAULT 'NORMALIZED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ux_living_normalized_item_source UNIQUE(source_item_id),
    CONSTRAINT ck_living_normalized_validation_needed CHECK (validation_needed_yn IN ('Y', 'N'))
);

CREATE INDEX IF NOT EXISTS idx_living_normalized_category
ON living_info.normalized_item(normalized_primary_category, normalized_secondary_category);

CREATE INDEX IF NOT EXISTS idx_living_normalized_topic_key_candidate
ON living_info.normalized_item(topic_key_candidate);

CREATE INDEX IF NOT EXISTS idx_living_normalized_usage_status
ON living_info.normalized_item(source_usage, status);

CREATE INDEX IF NOT EXISTS idx_living_normalized_signal_status
ON living_info.normalized_item(info_signal_type, status);

CREATE INDEX IF NOT EXISTS idx_living_normalized_scores
ON living_info.normalized_item(actionability_score DESC, repeatability_score DESC);

CREATE TABLE IF NOT EXISTS living_info.source_signal (
    id BIGSERIAL PRIMARY KEY,
    signal_source_name VARCHAR(200) NOT NULL DEFAULT '',
    signal_source_url TEXT NOT NULL DEFAULT '',
    signal_platform VARCHAR(80) NOT NULL DEFAULT '',
    signal_type VARCHAR(60) NOT NULL,
    language VARCHAR(20) NOT NULL DEFAULT '',
    country VARCHAR(80) NOT NULL DEFAULT 'Korea',
    region_in_korea VARCHAR(120) NOT NULL DEFAULT '',
    primary_category VARCHAR(60) NOT NULL,
    topic_key_candidate VARCHAR(180) NOT NULL DEFAULT '',
    target_user VARCHAR(120) NOT NULL DEFAULT '',
    pain_point_summary TEXT NOT NULL DEFAULT '',
    signal_count INTEGER NOT NULL DEFAULT 1,
    privacy_risk_level VARCHAR(40) NOT NULL DEFAULT 'MEDIUM',
    source_access_policy VARCHAR(60) NOT NULL DEFAULT 'PUBLIC_METADATA_ONLY',
    validation_needed_yn CHAR(1) NOT NULL DEFAULT 'Y',
    status VARCHAR(40) NOT NULL DEFAULT 'SIGNAL_COLLECTED',
    observed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT ck_living_source_signal_validation_needed CHECK (validation_needed_yn IN ('Y', 'N')),
    CONSTRAINT ck_living_source_signal_count CHECK (signal_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_living_source_signal_topic_observed
ON living_info.source_signal(topic_key_candidate, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_living_source_signal_category_observed
ON living_info.source_signal(primary_category, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_living_source_signal_type_status
ON living_info.source_signal(signal_type, status);

CREATE INDEX IF NOT EXISTS idx_living_source_signal_privacy
ON living_info.source_signal(privacy_risk_level);

CREATE TABLE IF NOT EXISTS living_info.topic_cluster (
    id BIGSERIAL PRIMARY KEY,
    topic_key VARCHAR(180) NOT NULL,
    primary_category VARCHAR(60) NOT NULL,
    secondary_category VARCHAR(120) NOT NULL DEFAULT '',
    target_user VARCHAR(120) NOT NULL DEFAULT '',
    action_type VARCHAR(120) NOT NULL DEFAULT '',
    source_count INTEGER NOT NULL DEFAULT 0,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    community_signal_count INTEGER NOT NULL DEFAULT 0,
    official_source_count INTEGER NOT NULL DEFAULT 0,
    secondary_source_count INTEGER NOT NULL DEFAULT 0,
    source_spread_count INTEGER NOT NULL DEFAULT 0,
    readiness_score NUMERIC(8,4) NOT NULL DEFAULT 0,
    public_candidate_ready_yn CHAR(1) NOT NULL DEFAULT 'N',
    validation_status VARCHAR(40) NOT NULL DEFAULT 'PENDING',
    cluster_status VARCHAR(40) NOT NULL DEFAULT 'OPEN',
    last_signal_at TIMESTAMPTZ,
    last_evidence_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ux_living_topic_cluster_identity UNIQUE(topic_key, primary_category, target_user, action_type),
    CONSTRAINT ck_living_topic_cluster_public_ready CHECK (public_candidate_ready_yn IN ('Y', 'N')),
    CONSTRAINT ck_living_topic_cluster_source_count CHECK (source_count >= 0),
    CONSTRAINT ck_living_topic_cluster_evidence_count CHECK (evidence_count >= 0),
    CONSTRAINT ck_living_topic_cluster_community_count CHECK (community_signal_count >= 0),
    CONSTRAINT ck_living_topic_cluster_official_count CHECK (official_source_count >= 0),
    CONSTRAINT ck_living_topic_cluster_secondary_count CHECK (secondary_source_count >= 0),
    CONSTRAINT ck_living_topic_cluster_spread_count CHECK (source_spread_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_category_readiness
ON living_info.topic_cluster(primary_category, readiness_score DESC);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_ready_readiness
ON living_info.topic_cluster(public_candidate_ready_yn, readiness_score DESC);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_validation_status
ON living_info.topic_cluster(validation_status, cluster_status);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_last_signal
ON living_info.topic_cluster(last_signal_at DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_last_evidence
ON living_info.topic_cluster(last_evidence_at DESC NULLS LAST);

CREATE TABLE IF NOT EXISTS living_info.topic_cluster_item (
    id BIGSERIAL PRIMARY KEY,
    topic_cluster_id BIGINT NOT NULL REFERENCES living_info.topic_cluster(id),
    normalized_item_id BIGINT REFERENCES living_info.normalized_item(id),
    source_signal_id BIGINT REFERENCES living_info.source_signal(id),
    item_role VARCHAR(60) NOT NULL,
    weight_score NUMERIC(8,4) NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_living_topic_cluster_item_one_source CHECK (
        (normalized_item_id IS NOT NULL AND source_signal_id IS NULL)
        OR (normalized_item_id IS NULL AND source_signal_id IS NOT NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_living_topic_cluster_item_normalized
ON living_info.topic_cluster_item(topic_cluster_id, normalized_item_id)
WHERE normalized_item_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_living_topic_cluster_item_signal
ON living_info.topic_cluster_item(topic_cluster_id, source_signal_id)
WHERE source_signal_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_item_role
ON living_info.topic_cluster_item(topic_cluster_id, item_role);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_item_normalized
ON living_info.topic_cluster_item(normalized_item_id);

CREATE INDEX IF NOT EXISTS idx_living_topic_cluster_item_signal
ON living_info.topic_cluster_item(source_signal_id);

-- Verification queries to run only when the migration is intentionally applied:
--
-- SELECT table_schema, table_name
-- FROM information_schema.tables
-- WHERE table_schema = 'living_info'
-- ORDER BY table_name;
--
-- SELECT indexname
-- FROM pg_indexes
-- WHERE schemaname = 'living_info'
-- ORDER BY indexname;
--
-- SELECT
--     tc.table_schema,
--     tc.table_name,
--     tc.constraint_name,
--     tc.constraint_type
-- FROM information_schema.table_constraints tc
-- WHERE tc.table_schema = 'living_info'
-- ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;
--
-- Rollback guidance:
--   This migration is additive. Do not automate destructive rollback.
--   In local/dev only and with explicit approval, remove the schema manually in a
--   separate rollback action. In shared or production-like environments, disable
--   the write path and leave tables in place until a reviewed rollback plan exists.
