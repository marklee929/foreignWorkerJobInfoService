package fwj.aniss.api.content.repository;

import java.sql.Types;
import java.util.List;
import java.util.Optional;

import org.springframework.dao.support.DataAccessUtils;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import fwj.aniss.api.content.entity.SourceItem;
import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class SourceItemRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public SourceItem save(SourceItem item) {
        String sql = """
                INSERT INTO content.source_item (
                    source_domain, source_platform, source_name, source_url, canonical_url,
                    publishable_link_url, title, body_text, summary_text, language, country_code,
                    category, subcategory, collected_at, last_seen_at, source_published_at,
                    raw_payload, source_risk_level, access_restriction, copyright_risk_level,
                    pii_checked_yn, usable_for_content_yn
                ) VALUES (
                    :sourceDomain, :sourcePlatform, :sourceName, :sourceUrl, :canonicalUrl,
                    :publishableLinkUrl, :title, :bodyText, :summaryText, :language, :countryCode,
                    :category, :subcategory, COALESCE(:collectedAt, CURRENT_TIMESTAMP), :lastSeenAt,
                    :sourcePublishedAt, CAST(:rawPayload AS jsonb), :sourceRiskLevel,
                    :accessRestriction, :copyrightRiskLevel, :piiCheckedYn, :usableForContentYn
                )
                """;
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(sql, params(item), keyHolder, new String[] { "id" });
        Number key = keyHolder.getKey();
        item.setId(key == null ? null : key.longValue());
        return item;
    }

    public Optional<SourceItem> findById(Long id) {
        String sql = "SELECT * FROM content.source_item WHERE id = :id";
        SourceItem item = DataAccessUtils.singleResult(
                jdbcTemplate.query(sql, new MapSqlParameterSource("id", id), ContentRowMapper::mapSourceItem));
        return Optional.ofNullable(item);
    }

    public Optional<SourceItem> findByDomainAndUrl(String sourceDomain, String canonicalUrl, String sourceUrl) {
        String url = defaultString(canonicalUrl, defaultString(sourceUrl, ""));
        if (url.isBlank()) {
            return Optional.empty();
        }
        String sql = """
                SELECT *
                FROM content.source_item
                WHERE source_domain = :sourceDomain
                  AND md5(COALESCE(NULLIF(canonical_url, ''), NULLIF(source_url, ''), '')) = md5(:url)
                ORDER BY id DESC
                LIMIT 1
                """;
        SourceItem item = DataAccessUtils.singleResult(
                jdbcTemplate.query(sql, new MapSqlParameterSource()
                        .addValue("sourceDomain", sourceDomain)
                        .addValue("url", url), ContentRowMapper::mapSourceItem));
        return Optional.ofNullable(item);
    }

    public void touchLastSeen(Long id) {
        String sql = """
                UPDATE content.source_item
                SET last_seen_at = CURRENT_TIMESTAMP
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, new MapSqlParameterSource("id", id));
    }

    public List<SourceItem> findPendingForGeneration(int limit) {
        String sql = """
                SELECT si.*
                FROM content.source_item si
                WHERE si.usable_for_content_yn = TRUE
                  AND NOT EXISTS (
                      SELECT 1
                      FROM content.generated_content gc
                      WHERE gc.source_item_id = si.id
                        AND gc.status <> 'COLLECTED'
                  )
                ORDER BY si.collected_at DESC, si.id DESC
                LIMIT :limit
                """;
        return jdbcTemplate.query(sql, new MapSqlParameterSource("limit", clampLimit(limit)),
                ContentRowMapper::mapSourceItem);
    }

    public List<SourceItem> list(String domain, String category, int limit, int offset) {
        StringBuilder sql = new StringBuilder("SELECT * FROM content.source_item WHERE 1 = 1");
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("limit", clampLimit(limit))
                .addValue("offset", Math.max(0, offset));

        if (domain != null && !domain.isBlank()) {
            sql.append(" AND source_domain = :domain");
            params.addValue("domain", domain);
        }
        if (category != null && !category.isBlank()) {
            sql.append(" AND category = :category");
            params.addValue("category", category);
        }
        sql.append(" ORDER BY collected_at DESC, id DESC LIMIT :limit OFFSET :offset");
        return jdbcTemplate.query(sql.toString(), params, ContentRowMapper::mapSourceItem);
    }

    private MapSqlParameterSource params(SourceItem item) {
        return new MapSqlParameterSource()
                .addValue("sourceDomain", defaultString(item.getSourceDomain(), "SOCIAL_NEWS"))
                .addValue("sourcePlatform", defaultString(item.getSourcePlatform(), ""))
                .addValue("sourceName", defaultString(item.getSourceName(), ""))
                .addValue("sourceUrl", defaultString(item.getSourceUrl(), ""))
                .addValue("canonicalUrl", defaultString(item.getCanonicalUrl(), ""))
                .addValue("publishableLinkUrl", defaultString(item.getPublishableLinkUrl(), ""))
                .addValue("title", defaultString(item.getTitle(), "Untitled source"))
                .addValue("bodyText", defaultString(item.getBodyText(), ""))
                .addValue("summaryText", defaultString(item.getSummaryText(), ""))
                .addValue("language", defaultString(item.getLanguage(), "ko"))
                .addValue("countryCode", defaultString(item.getCountryCode(), "KR"))
                .addValue("category", defaultString(item.getCategory(), ""))
                .addValue("subcategory", defaultString(item.getSubcategory(), ""))
                .addValue("collectedAt", item.getCollectedAt(), Types.TIMESTAMP_WITH_TIMEZONE)
                .addValue("lastSeenAt", item.getLastSeenAt(), Types.TIMESTAMP_WITH_TIMEZONE)
                .addValue("sourcePublishedAt", item.getSourcePublishedAt(), Types.TIMESTAMP_WITH_TIMEZONE)
                .addValue("rawPayload", defaultJson(item.getRawPayload()))
                .addValue("sourceRiskLevel", defaultString(item.getSourceRiskLevel(), "LOW"))
                .addValue("accessRestriction", defaultString(item.getAccessRestriction(), "PUBLIC"))
                .addValue("copyrightRiskLevel", defaultString(item.getCopyrightRiskLevel(), "LOW"))
                .addValue("piiCheckedYn", Boolean.TRUE.equals(item.getPiiCheckedYn()))
                .addValue("usableForContentYn", Boolean.TRUE.equals(item.getUsableForContentYn()));
    }

    private int clampLimit(int limit) {
        if (limit <= 0) {
            return 50;
        }
        return Math.min(limit, 500);
    }

    private String defaultString(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private String defaultJson(String value) {
        return value == null || value.isBlank() ? "{}" : value;
    }
}
