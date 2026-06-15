SELECT 'schema.content' AS check_name, COUNT(*)::text AS check_value
FROM information_schema.schemata
WHERE schema_name = 'content';

SELECT 'table.count' AS check_name, COUNT(*)::text AS check_value
FROM information_schema.tables
WHERE table_schema = 'content'
  AND table_name IN ('source_item', 'generated_content', 'review_log', 'publish_target', 'community_signal');

SELECT 'required.tables' AS check_name, string_agg(table_name, ', ' ORDER BY table_name) AS check_value
FROM information_schema.tables
WHERE table_schema = 'content'
  AND table_name IN ('source_item', 'generated_content', 'review_log', 'publish_target', 'community_signal');

SELECT 'primary.keys' AS check_name, COUNT(*)::text AS check_value
FROM information_schema.table_constraints
WHERE table_schema = 'content'
  AND constraint_type = 'PRIMARY KEY'
  AND table_name IN ('source_item', 'generated_content', 'review_log', 'publish_target', 'community_signal');

SELECT 'foreign.keys' AS check_name, COUNT(*)::text AS check_value
FROM information_schema.table_constraints
WHERE table_schema = 'content'
  AND constraint_type = 'FOREIGN KEY'
  AND table_name IN ('generated_content', 'review_log', 'publish_target');

SELECT 'unique.keys' AS check_name, COUNT(*)::text AS check_value
FROM information_schema.table_constraints
WHERE table_schema = 'content'
  AND constraint_type = 'UNIQUE'
  AND table_name = 'publish_target';

SELECT 'required.indexes' AS check_name, COUNT(*)::text AS check_value
FROM pg_indexes
WHERE schemaname = 'content'
  AND indexname IN (
      'idx_source_item_domain_collected',
      'idx_source_item_category',
      'idx_source_item_usable',
      'ux_source_item_domain_url_hash',
      'idx_generated_content_status',
      'idx_generated_content_category',
      'idx_generated_content_source',
      'ux_generated_content_source_item',
      'idx_generated_content_telegram',
      'idx_generated_content_collected_queue',
      'idx_generated_content_telegram_queue',
      'idx_generated_content_approval_queue',
      'idx_generated_content_approved',
      'idx_review_log_content',
      'idx_review_log_action',
      'idx_review_log_telegram_message',
      'idx_publish_target_content',
      'idx_publish_target_status',
      'idx_community_signal_topic',
      'idx_community_signal_score',
      'idx_community_signal_usable'
  );

SELECT indexname AS check_name, indexdef AS check_value
FROM pg_indexes
WHERE schemaname = 'content'
  AND indexname IN (
      'ux_source_item_domain_url_hash',
      'ux_generated_content_source_item',
      'idx_generated_content_collected_queue',
      'idx_generated_content_telegram_queue',
      'idx_generated_content_approval_queue',
      'idx_generated_content_approved',
      'idx_review_log_telegram_message'
  )
ORDER BY indexname;

SELECT 'invalid.generated_status' AS check_name, COUNT(*)::text AS check_value
FROM content.generated_content
WHERE status NOT IN ('COLLECTED', 'GENERATED', 'SENT_TO_TELEGRAM', 'APPROVED', 'REJECTED', 'PUBLISHED');

SELECT 'invalid.source_risk' AS check_name, COUNT(*)::text AS check_value
FROM content.source_item
WHERE source_risk_level NOT IN ('LOW', 'MEDIUM', 'HIGH', 'UNKNOWN');

SELECT 'duplicate.source_domain_url_hash' AS check_name, COUNT(*)::text AS check_value
FROM (
    SELECT source_domain, md5(COALESCE(NULLIF(canonical_url, ''), NULLIF(source_url, ''), '')) AS url_hash
    FROM content.source_item
    WHERE COALESCE(NULLIF(canonical_url, ''), NULLIF(source_url, '')) IS NOT NULL
    GROUP BY source_domain, md5(COALESCE(NULLIF(canonical_url, ''), NULLIF(source_url, ''), ''))
    HAVING COUNT(*) > 1
) duplicates;

SELECT 'generated.status_counts' AS check_name, COALESCE(jsonb_object_agg(status, count ORDER BY status), '{}'::jsonb)::text AS check_value
FROM (
    SELECT status, COUNT(*) AS count
    FROM content.generated_content
    GROUP BY status
) counts;

SELECT 'sample.rows' AS check_name, COUNT(*)::text AS check_value
FROM content.source_item
WHERE source_url LIKE 'https://local.workconnect/sample/%';
