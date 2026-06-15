WITH sample_source AS (
    SELECT *
    FROM (
        VALUES
            (
                'EMPLOYMENT',
                'work24',
                'Work24',
                'https://local.workconnect/sample/work24-generated',
                'https://local.workconnect/sample/work24-generated',
                'https://local.workconnect/sample/work24-generated',
                'Work24 sample job information for foreign workers',
                'A local sample source item for validating the generated content queue. It includes work location, salary basis and source verification reminders.',
                'Sample employment source for GENERATED queue validation.',
                'en',
                'KR',
                'employment',
                'sample_generated',
                '{"sample":true,"queue":"GENERATED"}'::jsonb,
                'LOW',
                'PUBLIC',
                'LOW',
                TRUE,
                TRUE
            ),
            (
                'VISA_IMMIGRATION',
                'hikorea',
                'HiKorea',
                'https://local.workconnect/sample/hikorea-sent',
                'https://local.workconnect/sample/hikorea-sent',
                'https://local.workconnect/sample/hikorea-sent',
                'HiKorea sample visa checklist',
                'A local sample source item for validating Telegram delivery and SENT_TO_TELEGRAM review queue behavior.',
                'Sample visa source for SENT_TO_TELEGRAM queue validation.',
                'en',
                'KR',
                'visa',
                'sample_sent',
                '{"sample":true,"queue":"SENT_TO_TELEGRAM"}'::jsonb,
                'MEDIUM',
                'PUBLIC',
                'LOW',
                TRUE,
                TRUE
            ),
            (
                'LIVING_INFO',
                'housing',
                'Housing',
                'https://local.workconnect/sample/housing-approved',
                'https://local.workconnect/sample/housing-approved',
                'https://local.workconnect/sample/housing-approved',
                'Housing sample contract checklist',
                'A local sample source item for validating APPROVED queue behavior after admin or Telegram review.',
                'Sample housing source for APPROVED queue validation.',
                'en',
                'KR',
                'housing',
                'sample_approved',
                '{"sample":true,"queue":"APPROVED"}'::jsonb,
                'MEDIUM',
                'PUBLIC',
                'LOW',
                TRUE,
                TRUE
            ),
            (
                'LIVING_INFO',
                'finance',
                'Finance',
                'https://local.workconnect/sample/finance-rejected',
                'https://local.workconnect/sample/finance-rejected',
                'https://local.workconnect/sample/finance-rejected',
                'Finance sample bank account checklist',
                'A local sample source item for validating REJECTED queue behavior and review log display.',
                'Sample finance source for REJECTED queue validation.',
                'en',
                'KR',
                'finance',
                'sample_rejected',
                '{"sample":true,"queue":"REJECTED"}'::jsonb,
                'MEDIUM',
                'PUBLIC',
                'LOW',
                TRUE,
                TRUE
            )
    ) AS v (
        source_domain,
        source_platform,
        source_name,
        source_url,
        canonical_url,
        publishable_link_url,
        title,
        body_text,
        summary_text,
        language,
        country_code,
        category,
        subcategory,
        raw_payload,
        source_risk_level,
        access_restriction,
        copyright_risk_level,
        pii_checked_yn,
        usable_for_content_yn
    )
)
INSERT INTO content.source_item (
    source_domain,
    source_platform,
    source_name,
    source_url,
    canonical_url,
    publishable_link_url,
    title,
    body_text,
    summary_text,
    language,
    country_code,
    category,
    subcategory,
    raw_payload,
    source_risk_level,
    access_restriction,
    copyright_risk_level,
    pii_checked_yn,
    usable_for_content_yn,
    collected_at,
    last_seen_at
)
SELECT
    source_domain,
    source_platform,
    source_name,
    source_url,
    canonical_url,
    publishable_link_url,
    title,
    body_text,
    summary_text,
    language,
    country_code,
    category,
    subcategory,
    raw_payload,
    source_risk_level,
    access_restriction,
    copyright_risk_level,
    pii_checked_yn,
    usable_for_content_yn,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
FROM sample_source s
WHERE NOT EXISTS (
    SELECT 1
    FROM content.source_item existing
    WHERE existing.source_domain = s.source_domain
      AND md5(COALESCE(NULLIF(existing.canonical_url, ''), NULLIF(existing.source_url, ''), '')) = md5(s.canonical_url)
);

WITH source_rows AS (
    SELECT *
    FROM content.source_item
    WHERE source_url IN (
        'https://local.workconnect/sample/work24-generated',
        'https://local.workconnect/sample/hikorea-sent',
        'https://local.workconnect/sample/housing-approved',
        'https://local.workconnect/sample/finance-rejected'
    )
),
sample_generated AS (
    SELECT
        si.id AS source_item_id,
        CASE si.source_platform
            WHEN 'work24' THEN 'JOB_GUIDE'
            WHEN 'hikorea' THEN 'VISA_GUIDE'
            ELSE 'LIVING_TIP'
        END AS content_type,
        si.category,
        si.subcategory,
        'foreign workers and residents in Korea' AS target_persona,
        'en' AS language,
        si.title AS title,
        (
            si.title || E'\n\nSummary\n' || si.summary_text ||
            E'\n\nWhy it matters\nLocal sample data validates the content approval queue without external services.' ||
            E'\n\nCheck next\n1. Confirm the original source link.\n2. Run Telegram dry-run delivery.\n3. Approve or reject from Admin UI.'
        ) AS written_content,
        si.summary_text AS short_summary,
        'Local sample data validates the content approval queue without external services.' AS why_it_matters,
        E'1. Confirm the original source link.\n2. Run Telegram dry-run delivery.\n3. Approve or reject from Admin UI.' AS check_next,
        '#WorkConnectKorea #LocalMVP #' || regexp_replace(si.category, '[^A-Za-z0-9]', '', 'g') AS hashtags,
        '' AS image_url,
        'Clean editorial image for local validation: ' || si.category AS image_prompt,
        'Local sample data only. Verify official sources before using content publicly.' AS source_disclaimer,
        FALSE AS translation_yn,
        '' AS translated_from,
        si.publishable_link_url AS original_link,
        'rule-based-mvp-sample' AS generation_model,
        CASE si.source_risk_level WHEN 'LOW' THEN 82.00 ELSE 72.00 END::numeric AS quality_score,
        CASE si.source_risk_level WHEN 'LOW' THEN 20.00 ELSE 50.00 END::numeric AS risk_score,
        CASE si.source_platform
            WHEN 'work24' THEN 'GENERATED'
            WHEN 'hikorea' THEN 'SENT_TO_TELEGRAM'
            WHEN 'housing' THEN 'APPROVED'
            WHEN 'finance' THEN 'REJECTED'
        END AS status,
        CASE si.source_platform
            WHEN 'work24' THEN 'Sample generated draft.'
            WHEN 'hikorea' THEN 'Sample sent to Telegram dry-run.'
            WHEN 'housing' THEN 'Sample approved content.'
            WHEN 'finance' THEN 'Sample rejected content.'
        END AS status_reason,
        CASE si.source_platform
            WHEN 'hikorea' THEN 700001
            WHEN 'housing' THEN 700002
            WHEN 'finance' THEN 700003
            ELSE NULL
        END::bigint AS telegram_message_id,
        CASE si.source_platform WHEN 'housing' THEN 'sample-admin' WHEN 'finance' THEN 'sample-admin' ELSE '' END AS reviewer_id,
        CASE si.source_platform WHEN 'housing' THEN 'Sample Admin' WHEN 'finance' THEN 'Sample Admin' ELSE '' END AS reviewer_name,
        CASE si.source_platform WHEN 'housing' THEN CURRENT_TIMESTAMP ELSE NULL END AS approved_at,
        CASE si.source_platform WHEN 'finance' THEN CURRENT_TIMESTAMP ELSE NULL END AS rejected_at
    FROM source_rows si
)
INSERT INTO content.generated_content (
    source_item_id,
    content_type,
    category,
    subcategory,
    target_persona,
    language,
    title,
    written_content,
    short_summary,
    why_it_matters,
    check_next,
    hashtags,
    image_url,
    image_prompt,
    source_disclaimer,
    translation_yn,
    translated_from,
    original_link,
    generated_at,
    generation_model,
    quality_score,
    risk_score,
    status,
    status_reason,
    telegram_message_id,
    reviewer_id,
    reviewer_name,
    approved_at,
    rejected_at
)
SELECT
    source_item_id,
    content_type,
    category,
    subcategory,
    target_persona,
    language,
    title,
    written_content,
    short_summary,
    why_it_matters,
    check_next,
    hashtags,
    image_url,
    image_prompt,
    source_disclaimer,
    translation_yn,
    translated_from,
    original_link,
    CURRENT_TIMESTAMP,
    generation_model,
    quality_score,
    risk_score,
    status,
    status_reason,
    telegram_message_id,
    reviewer_id,
    reviewer_name,
    approved_at,
    rejected_at
FROM sample_generated
ON CONFLICT DO NOTHING;

INSERT INTO content.review_log (
    generated_content_id,
    review_channel,
    telegram_message_id,
    reviewer_id,
    reviewer_name,
    action,
    comment
)
SELECT
    gc.id,
    'ADMIN',
    gc.telegram_message_id,
    COALESCE(NULLIF(gc.reviewer_id, ''), 'sample-admin'),
    COALESCE(NULLIF(gc.reviewer_name, ''), 'Sample Admin'),
    CASE gc.status
        WHEN 'SENT_TO_TELEGRAM' THEN 'SENT'
        WHEN 'APPROVED' THEN 'APPROVED'
        WHEN 'REJECTED' THEN 'REJECTED'
        ELSE 'SENT'
    END,
    'Local sample review log for ' || gc.status
FROM content.generated_content gc
JOIN content.source_item si ON si.id = gc.source_item_id
WHERE si.source_url IN (
    'https://local.workconnect/sample/hikorea-sent',
    'https://local.workconnect/sample/housing-approved',
    'https://local.workconnect/sample/finance-rejected'
)
AND NOT EXISTS (
    SELECT 1
    FROM content.review_log rl
    WHERE rl.generated_content_id = gc.id
      AND rl.action = CASE gc.status
          WHEN 'SENT_TO_TELEGRAM' THEN 'SENT'
          WHEN 'APPROVED' THEN 'APPROVED'
          WHEN 'REJECTED' THEN 'REJECTED'
          ELSE 'SENT'
      END
);

INSERT INTO content.publish_target (
    generated_content_id,
    target_channel,
    publish_status
)
SELECT gc.id, target_channel, 'PENDING'
FROM content.generated_content gc
JOIN content.source_item si ON si.id = gc.source_item_id
CROSS JOIN (VALUES ('FACEBOOK'), ('SITE')) AS targets(target_channel)
WHERE si.source_url IN (
    'https://local.workconnect/sample/work24-generated',
    'https://local.workconnect/sample/hikorea-sent',
    'https://local.workconnect/sample/housing-approved',
    'https://local.workconnect/sample/finance-rejected'
)
ON CONFLICT (generated_content_id, target_channel) DO NOTHING;

INSERT INTO content.community_signal (
    source_platform,
    source_url,
    topic,
    language,
    country,
    category,
    question_pattern,
    frequency_score,
    urgency_score,
    sample_count,
    author_hash,
    raw_retention_policy,
    pii_checked_yn,
    usable_for_content_yn,
    terms_risk_level
)
SELECT *
FROM (
    VALUES
        (
            'reddit',
            'https://www.reddit.com/r/korea/',
            'Local sample signal: visa document checklist questions',
            'en',
            'KR',
            'community_signal',
            'What documents should I prepare before visiting immigration?',
            71.00::numeric,
            82.00::numeric,
            14,
            '',
            'ANONYMIZED_SUMMARY_ONLY',
            TRUE,
            TRUE,
            'HIGH'
        ),
        (
            'public_community_trend',
            '',
            'Local sample signal: housing deposit safety questions',
            'en',
            'KR',
            'community_signal',
            'What should I check before signing a housing contract?',
            64.00::numeric,
            70.00::numeric,
            11,
            '',
            'ANONYMIZED_SUMMARY_ONLY',
            TRUE,
            TRUE,
            'MEDIUM'
        )
) AS v (
    source_platform,
    source_url,
    topic,
    language,
    country,
    category,
    question_pattern,
    frequency_score,
    urgency_score,
    sample_count,
    author_hash,
    raw_retention_policy,
    pii_checked_yn,
    usable_for_content_yn,
    terms_risk_level
)
WHERE NOT EXISTS (
    SELECT 1
    FROM content.community_signal existing
    WHERE existing.topic = v.topic
      AND existing.source_platform = v.source_platform
);
