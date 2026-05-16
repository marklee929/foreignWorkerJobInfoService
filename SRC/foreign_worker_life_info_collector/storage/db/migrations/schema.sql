CREATE TABLE IF NOT EXISTS source_raw_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_url TEXT NOT NULL,
    search_keyword TEXT NOT NULL,
    raw_title TEXT NOT NULL,
    raw_content TEXT,
    raw_phone TEXT,
    raw_address TEXT,
    collected_at TEXT NOT NULL,
    hash_key TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS life_service_business (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    phone TEXT,
    address TEXT,
    sido TEXT,
    sigungu TEXT,
    latitude REAL,
    longitude REAL,
    website_url TEXT,
    kakao_url TEXT,
    naver_place_url TEXT,
    google_place_url TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS business_language_support (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    language_code TEXT NOT NULL,
    language_name TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    evidence_text TEXT,
    FOREIGN KEY (business_id) REFERENCES life_service_business(id)
);

CREATE TABLE IF NOT EXISTS business_service_tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    evidence_text TEXT,
    FOREIGN KEY (business_id) REFERENCES life_service_business(id)
);

CREATE TABLE IF NOT EXISTS crawl_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawler_name TEXT NOT NULL,
    keyword TEXT NOT NULL,
    status TEXT NOT NULL,
    collected_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS data_quality_score (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER,
    duplicate_score REAL NOT NULL,
    freshness_score REAL NOT NULL,
    contact_validity_score REAL NOT NULL,
    foreigner_relevance_score REAL NOT NULL,
    total_score REAL NOT NULL,
    calculated_at TEXT NOT NULL,
    FOREIGN KEY (business_id) REFERENCES life_service_business(id)
);
