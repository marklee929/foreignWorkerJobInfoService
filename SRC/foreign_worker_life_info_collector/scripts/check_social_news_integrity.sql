-- Social news pipeline integrity checks.
-- Run in PostgreSQL against the foreign_worker_job_info database.

-- 1. Table counts
SELECT 'raw_item' AS table_name, COUNT(*) AS row_count FROM social_news.raw_item
UNION ALL SELECT 'normalized_item', COUNT(*) FROM social_news.normalized_item
UNION ALL SELECT 'candidate', COUNT(*) FROM social_news.candidate
UNION ALL SELECT 'publish_log', COUNT(*) FROM social_news.publish_log
UNION ALL SELECT 'pipeline_step_log', COUNT(*) FROM social_news.pipeline_step_log;

-- 2. Daily counts
SELECT DATE(collected_at) AS day, COUNT(*) AS raw_count
FROM social_news.raw_item
GROUP BY DATE(collected_at)
ORDER BY day DESC;

SELECT DATE(normalized_at) AS day, COUNT(*) AS normalized_count
FROM social_news.normalized_item
GROUP BY DATE(normalized_at)
ORDER BY day DESC;

SELECT DATE(collected_at) AS day, COUNT(*) AS candidate_count
FROM social_news.candidate
GROUP BY DATE(collected_at)
ORDER BY day DESC;

-- 3. Candidate references
SELECT
    COUNT(*) AS total_candidates,
    COUNT(normalized_item_id) AS with_normalized_item,
    COUNT(*) FILTER (WHERE normalized_item_id IS NULL) AS without_normalized_item
FROM social_news.candidate;

SELECT candidate.id, candidate.title, candidate.source_url, candidate.collected_at
FROM social_news.candidate candidate
LEFT JOIN social_news.normalized_item normalized ON normalized.id = candidate.normalized_item_id
WHERE candidate.normalized_item_id IS NOT NULL
  AND normalized.id IS NULL
ORDER BY candidate.id DESC;

-- 4. Candidate duplication by normalized item and source URL
SELECT normalized_item_id, COUNT(*) AS candidate_count
FROM social_news.candidate
WHERE normalized_item_id IS NOT NULL
GROUP BY normalized_item_id
HAVING COUNT(*) > 1
ORDER BY candidate_count DESC;

SELECT source_url, COUNT(*) AS candidate_count
FROM social_news.candidate
WHERE source_url IS NOT NULL AND source_url <> ''
GROUP BY source_url
HAVING COUNT(*) > 1
ORDER BY candidate_count DESC;

-- 5. Raw occurrence grouping
SELECT source_hash, COUNT(*) AS raw_occurrence_count, MAX(collected_at) AS last_seen_at
FROM social_news.raw_item
WHERE source_hash IS NOT NULL
GROUP BY source_hash
HAVING COUNT(*) > 1
ORDER BY raw_occurrence_count DESC, last_seen_at DESC;

SELECT normalized_item_id, COUNT(*) AS raw_occurrence_count, MAX(collected_at) AS last_seen_at
FROM social_news.raw_item
WHERE normalized_item_id IS NOT NULL
GROUP BY normalized_item_id
ORDER BY raw_occurrence_count DESC, last_seen_at DESC;

-- 6. Similarity key grouping
SELECT similarity_key, COUNT(*) AS normalized_count
FROM social_news.normalized_item
WHERE similarity_key IS NOT NULL AND similarity_key <> ''
GROUP BY similarity_key
HAVING COUNT(*) > 1
ORDER BY normalized_count DESC;

-- 7. Representative candidate grouping
SELECT
    COUNT(*) AS total_candidates,
    COUNT(*) FILTER (WHERE COALESCE(is_representative, TRUE)) AS representative_candidates,
    COUNT(*) FILTER (WHERE NOT COALESCE(is_representative, TRUE)) AS hidden_duplicate_candidates
FROM social_news.candidate;

SELECT id, title, normalized_item_id, group_item_count, duplicate_count, related_source_count, last_seen_at
FROM social_news.candidate
WHERE COALESCE(is_representative, TRUE)
ORDER BY COALESCE(last_seen_at, collected_at) DESC, id DESC
LIMIT 100;

-- 8. Cleanup/delete trace by visible remaining data.
-- PostgreSQL cannot show deleted rows without audit triggers, so this checks current retention state.
SELECT
    COUNT(*) FILTER (WHERE post_expired) AS post_expired_count,
    COUNT(*) FILTER (WHERE publish_status = 'POST_EXPIRED') AS post_expired_status_count,
    COUNT(*) FILTER (WHERE publish_status = 'READY_TO_PUBLISH') AS ready_count,
    COUNT(*) FILTER (WHERE published_at IS NOT NULL OR facebook_post_url IS NOT NULL) AS posted_count
FROM social_news.candidate;
