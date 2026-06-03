CREATE SCHEMA IF NOT EXISTS occupation;

CREATE TABLE IF NOT EXISTS occupation.job_info (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(80) NOT NULL DEFAULT 'employment24',
    job_code VARCHAR(80) NOT NULL,
    job_name_ko VARCHAR(300) NOT NULL,
    job_name_en VARCHAR(300),
    job_category_code VARCHAR(80),
    job_category_name VARCHAR(300),
    description_ko TEXT,
    description_en TEXT,
    required_skills TEXT,
    related_keywords TEXT,
    raw_response JSONB NOT NULL DEFAULT '{}'::jsonb,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active_yn CHAR(1) NOT NULL DEFAULT 'Y',
    CONSTRAINT uq_occupation_job_info_source_code UNIQUE(source, job_code)
);

CREATE TABLE IF NOT EXISTS occupation.occupation_info (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(80) NOT NULL DEFAULT 'employment24',
    occupation_code VARCHAR(80) NOT NULL,
    occupation_name_ko VARCHAR(300) NOT NULL,
    occupation_name_en VARCHAR(300),
    occupation_category_code VARCHAR(80),
    occupation_category_name VARCHAR(300),
    work_description_ko TEXT,
    work_description_en TEXT,
    required_education TEXT,
    required_certificates TEXT,
    related_jobs TEXT,
    outlook TEXT,
    raw_response JSONB NOT NULL DEFAULT '{}'::jsonb,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active_yn CHAR(1) NOT NULL DEFAULT 'Y',
    CONSTRAINT uq_occupation_info_source_code UNIQUE(source, occupation_code)
);

CREATE TABLE IF NOT EXISTS occupation.keyword_mapping (
    id BIGSERIAL PRIMARY KEY,
    language_code VARCHAR(20) NOT NULL,
    external_keyword VARCHAR(300) NOT NULL,
    normalized_keyword VARCHAR(300) NOT NULL,
    keyword_type VARCHAR(40) NOT NULL DEFAULT 'rule',
    job_code VARCHAR(80),
    occupation_code VARCHAR(80),
    mapped_name_ko VARCHAR(300),
    mapped_name_en VARCHAR(300),
    match_score NUMERIC(8,4) NOT NULL DEFAULT 1.0,
    mapping_source VARCHAR(80) NOT NULL DEFAULT 'seed',
    priority INTEGER NOT NULL DEFAULT 100,
    active_yn CHAR(1) NOT NULL DEFAULT 'Y',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS occupation.collect_log (
    id BIGSERIAL PRIMARY KEY,
    collector_type VARCHAR(40) NOT NULL,
    status VARCHAR(40) NOT NULL,
    requested_count INTEGER NOT NULL DEFAULT 0,
    inserted_count INTEGER NOT NULL DEFAULT 0,
    updated_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    error_message TEXT,
    request_params JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS occupation.raw_api_response (
    id BIGSERIAL PRIMARY KEY,
    collector_type VARCHAR(40) NOT NULL,
    request_url_without_key TEXT,
    response_body TEXT,
    parsed_yn CHAR(1) NOT NULL DEFAULT 'N',
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_occupation_job_info_name ON occupation.job_info(job_name_ko);
CREATE INDEX IF NOT EXISTS idx_occupation_job_info_active ON occupation.job_info(active_yn);
CREATE INDEX IF NOT EXISTS idx_occupation_info_name ON occupation.occupation_info(occupation_name_ko);
CREATE INDEX IF NOT EXISTS idx_occupation_info_active ON occupation.occupation_info(active_yn);
CREATE INDEX IF NOT EXISTS idx_occupation_keyword_mapping_keyword ON occupation.keyword_mapping(language_code, normalized_keyword, active_yn);
CREATE UNIQUE INDEX IF NOT EXISTS uq_occupation_keyword_mapping
ON occupation.keyword_mapping(language_code, external_keyword, COALESCE(job_code, ''), COALESCE(occupation_code, ''));
CREATE INDEX IF NOT EXISTS idx_occupation_collect_log_type_started ON occupation.collect_log(collector_type, started_at DESC);

INSERT INTO occupation.keyword_mapping
    (language_code, external_keyword, normalized_keyword, keyword_type, mapped_name_ko, mapped_name_en, match_score, mapping_source, priority)
VALUES
    ('en', 'factory worker', 'factory worker', 'seed', '생산직', 'Factory worker', 0.95, 'seed', 10),
    ('en', 'manufacturing', 'manufacturing', 'seed', '제조업', 'Manufacturing', 0.90, 'seed', 20),
    ('en', 'welder', 'welder', 'seed', '용접원', 'Welder', 0.95, 'seed', 10),
    ('en', 'welding', 'welding', 'seed', '용접', 'Welding', 0.90, 'seed', 20),
    ('en', 'forklift driver', 'forklift driver', 'seed', '지게차 운전원', 'Forklift driver', 0.95, 'seed', 10),
    ('en', 'packing', 'packing', 'seed', '포장원', 'Packing worker', 0.90, 'seed', 20),
    ('en', 'cleaner', 'cleaner', 'seed', '청소원', 'Cleaner', 0.90, 'seed', 20),
    ('en', 'caregiver', 'caregiver', 'seed', '요양보호사', 'Caregiver', 0.90, 'seed', 20),
    ('en', 'construction worker', 'construction worker', 'seed', '건설 근로자', 'Construction worker', 0.90, 'seed', 20),
    ('en', 'farm worker', 'farm worker', 'seed', '농업 근로자', 'Farm worker', 0.90, 'seed', 20),
    ('en', 'kitchen assistant', 'kitchen assistant', 'seed', '주방보조', 'Kitchen assistant', 0.90, 'seed', 20),
    ('en', 'hotel staff', 'hotel staff', 'seed', '호텔 직원', 'Hotel staff', 0.85, 'seed', 30),
    ('en', 'CNC operator', 'cnc operator', 'seed', 'CNC 조작원', 'CNC operator', 0.95, 'seed', 10),
    ('en', 'machine operator', 'machine operator', 'seed', '기계 조작원', 'Machine operator', 0.90, 'seed', 20)
ON CONFLICT DO NOTHING;
