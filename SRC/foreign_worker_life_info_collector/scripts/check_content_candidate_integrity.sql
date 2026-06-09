-- Content candidate integrity checks for the admin publishing hub.
-- Run in PostgreSQL against the WorkConnect local database.

-- 1. raw_ref_table + raw_ref_id must be unique.
SELECT raw_ref_table, raw_ref_id, COUNT(*) AS row_count, array_agg(id ORDER BY id) AS content_candidate_ids
FROM content.content_candidate
GROUP BY raw_ref_table, raw_ref_id
HAVING COUNT(*) > 1
ORDER BY row_count DESC, raw_ref_table, raw_ref_id;

-- 2. Same title/source_url duplicated in visible content rows.
SELECT lower(title) AS normalized_title, COALESCE(NULLIF(source_url, ''), link_url) AS normalized_url,
       COUNT(*) AS row_count, array_agg(id ORDER BY id) AS content_candidate_ids
FROM content.content_candidate
WHERE status <> 'ARCHIVED'
GROUP BY lower(title), COALESCE(NULLIF(source_url, ''), link_url)
HAVING COUNT(*) > 1
ORDER BY row_count DESC, normalized_title;

-- 3. More than one visible content candidate in the same social_news duplicate group.
SELECT COALESCE(news.duplicate_group_id, news.representative_candidate_id, news.id) AS duplicate_group_id,
       COUNT(*) AS visible_content_count,
       array_agg(content_row.id ORDER BY content_row.id) AS content_candidate_ids,
       array_agg(news.id ORDER BY news.id) AS news_candidate_ids
FROM content.content_candidate content_row
JOIN social_news.candidate news
  ON content_row.raw_ref_table = 'social_news.candidate'
 AND content_row.raw_ref_id = news.id
WHERE content_row.status <> 'ARCHIVED'
GROUP BY COALESCE(news.duplicate_group_id, news.representative_candidate_id, news.id)
HAVING COUNT(*) > 1
ORDER BY visible_content_count DESC, duplicate_group_id;

-- 4. Content rows marked POSTED but missing the Facebook URL.
SELECT id, raw_ref_table, raw_ref_id, title, facebook_post_id, facebook_post_url, published_at
FROM content.content_candidate
WHERE status = 'POSTED'
  AND COALESCE(facebook_post_url, '') = ''
ORDER BY published_at DESC NULLS LAST, id DESC;

-- 5. social_news has a Facebook URL but the linked content row does not.
SELECT news.id AS news_candidate_id, content_row.id AS content_candidate_id,
       news.title, news.facebook_post_url AS news_facebook_post_url,
       content_row.facebook_post_url AS content_facebook_post_url,
       news.published_at AS news_published_at,
       content_row.published_at AS content_published_at
FROM social_news.candidate news
LEFT JOIN content.content_candidate content_row
  ON content_row.raw_ref_table = 'social_news.candidate'
 AND content_row.raw_ref_id = news.id
WHERE COALESCE(news.facebook_post_url, '') <> ''
  AND COALESCE(content_row.facebook_post_url, '') = ''
ORDER BY news.published_at DESC NULLS LAST, news.id DESC;

-- 6. Non-representative or duplicate social news still visible as content candidates.
SELECT content_row.id AS content_candidate_id, news.id AS news_candidate_id,
       content_row.status AS content_status, news.status AS news_status,
       news.publish_status, news.is_representative, news.duplicate_group_id, news.title
FROM content.content_candidate content_row
JOIN social_news.candidate news
  ON content_row.raw_ref_table = 'social_news.candidate'
 AND content_row.raw_ref_id = news.id
WHERE content_row.status <> 'ARCHIVED'
  AND (
      COALESCE(news.is_representative, TRUE) = FALSE
      OR COALESCE(news.publish_status, news.status, '') IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'SKIPPED', 'TEXT_INVALID', 'ARCHIVED')
      OR COALESCE(news.status, '') IN ('DUPLICATE', 'DUPLICATE_SKIPPED', 'SKIPPED', 'TEXT_INVALID', 'ARCHIVED')
  )
ORDER BY content_row.updated_at DESC, content_row.id DESC;
