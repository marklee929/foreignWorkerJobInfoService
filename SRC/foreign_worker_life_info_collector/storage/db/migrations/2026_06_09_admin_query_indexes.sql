CREATE INDEX IF NOT EXISTS idx_social_news_candidate_status
ON social_news.candidate(status);

CREATE INDEX IF NOT EXISTS idx_social_news_candidate_publish_status
ON social_news.candidate(publish_status);

CREATE INDEX IF NOT EXISTS idx_social_news_candidate_publish_cycle_id
ON social_news.candidate(publish_cycle_id);

CREATE INDEX IF NOT EXISTS idx_social_news_candidate_collected_at
ON social_news.candidate(collected_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_social_news_candidate_duplicate_group_id
ON social_news.candidate(duplicate_group_id);

CREATE INDEX IF NOT EXISTS idx_content_candidate_status
ON content.content_candidate(status);

CREATE INDEX IF NOT EXISTS idx_content_candidate_content_type
ON content.content_candidate(content_type);

CREATE INDEX IF NOT EXISTS idx_content_candidate_category
ON content.content_candidate(category);

CREATE INDEX IF NOT EXISTS idx_content_candidate_created_at
ON content.content_candidate(created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_content_candidate_raw_ref
ON content.content_candidate(raw_ref_table, raw_ref_id);

CREATE INDEX IF NOT EXISTS idx_social_news_pipeline_step_log_created_at
ON social_news.pipeline_step_log(created_at DESC, id DESC);

