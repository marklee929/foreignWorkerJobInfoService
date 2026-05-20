INSERT INTO admin.module_config
    (module_key, module_group, module_name, description, is_enabled, is_required, run_order, config_json)
VALUES
    ('collector.naver', 'collector', 'Naver News Collector', 'Collect candidate news from Naver or Naver-compatible search.', TRUE, FALSE, 10, '{"adapter":"NaverNewsCollector"}'),
    ('collector.google', 'collector', 'Google News Collector', 'Collect candidate news from Google News RSS.', TRUE, FALSE, 20, '{"adapter":"GoogleNewsCollector"}'),
    ('collector.rss', 'collector', 'RSS News Collector', 'Collect candidate news from configured RSS feeds.', FALSE, FALSE, 30, '{"adapter":"RssNewsCollector"}'),
    ('step.normalize', 'step', 'Normalize News', 'Strip HTML, canonicalize URL, extract source name, generate hashes.', TRUE, TRUE, 100, '{"required_before":"candidate_evaluation"}'),
    ('step.summarize', 'step', 'Summarize News', 'Generate plain text short summary and key points.', TRUE, FALSE, 110, '{"allow_llama":true}'),
    ('step.duplicate_check', 'step', 'Duplicate Check', 'Apply deterministic duplicate checks using URL, title hash, similarity key, and recent posts.', TRUE, TRUE, 120, '{"deterministic":true}'),
    ('step.llama_check', 'step', 'Local LLaMA Check', 'Optional semantic duplicate/relevance advisory when LOCAL_LLAMA_ENDPOINT exists.', FALSE, FALSE, 130, '{"env_key":"LOCAL_LLAMA_ENDPOINT","advisory_only":true}'),
    ('step.candidate_evaluation', 'step', 'Candidate Evaluation', 'Score candidates by Korea relevance, foreign worker relevance, freshness, reliability, and suitability.', TRUE, TRUE, 140, '{"selector":"CandidateEvaluator"}'),
    ('publish.facebook', 'publish', 'Facebook Publish', 'Publish selected news to Facebook Page only when real mode and env are valid.', FALSE, FALSE, 200, '{"dry_run_default":true}'),
    ('notify.telegram', 'notify', 'Telegram Notify', 'Send publish result notification. This is not an approval channel.', FALSE, FALSE, 210, '{"approval_flow":false}')
ON CONFLICT (module_key) DO UPDATE SET
    module_group = EXCLUDED.module_group,
    module_name = EXCLUDED.module_name,
    description = EXCLUDED.description,
    is_required = EXCLUDED.is_required,
    run_order = EXCLUDED.run_order,
    config_json = EXCLUDED.config_json,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO admin.runtime_config
    (config_key, config_value, value_type, is_sensitive, description)
VALUES
    ('news.default_keyword', '외국인 취업 비자', 'string', FALSE, 'Default search keyword for social news automation.'),
    ('news.default_limit', '1', 'integer', FALSE, 'Maximum selected candidates per cycle.'),
    ('news.default_dry_run', 'true', 'boolean', FALSE, 'Dry-run is the default execution mode.'),
    ('ui.refresh_interval_seconds', '15', 'integer', FALSE, 'Suggested dashboard polling interval.'),
    ('pipeline.real_publish_requires_ui_toggle', 'true', 'boolean', FALSE, 'Real publish requires explicit UI/admin activation.')
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    value_type = EXCLUDED.value_type,
    is_sensitive = EXCLUDED.is_sensitive,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

INSERT INTO admin.env_status
    (env_key, module_key, is_required, is_configured, status, message)
VALUES
    ('FACEBOOK_PAGE_ID', 'publish.facebook', TRUE, FALSE, 'UNKNOWN', 'Required only for real Facebook publish. Do not store the value in DB.'),
    ('FACEBOOK_PAGE_ACCESS_TOKEN', 'publish.facebook', TRUE, FALSE, 'UNKNOWN', 'Required only for real Facebook publish. Do not store the value in DB.'),
    ('TELEGRAM_BOT_TOKEN', 'notify.telegram', TRUE, FALSE, 'UNKNOWN', 'Required only for real Telegram notification. Do not store the value in DB.'),
    ('TELEGRAM_CHAT_ID', 'notify.telegram', TRUE, FALSE, 'UNKNOWN', 'Required only for real Telegram notification. Do not store the value in DB.'),
    ('LOCAL_LLAMA_ENDPOINT', 'step.llama_check', FALSE, FALSE, 'UNKNOWN', 'Optional. If missing or timeout, deterministic rules remain active.')
ON CONFLICT (env_key) DO UPDATE SET
    module_key = EXCLUDED.module_key,
    is_required = EXCLUDED.is_required,
    message = EXCLUDED.message;
