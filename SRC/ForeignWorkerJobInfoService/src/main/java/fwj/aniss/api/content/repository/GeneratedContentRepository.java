package fwj.aniss.api.content.repository;

import java.sql.Types;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.dao.support.DataAccessUtils;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import fwj.aniss.api.content.entity.GeneratedContent;
import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class GeneratedContentRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public GeneratedContent save(GeneratedContent content) {
        String sql = """
                INSERT INTO content.generated_content (
                    source_item_id, content_type, category, subcategory, target_persona, language,
                    title, written_content, short_summary, why_it_matters, check_next, hashtags,
                    image_url, image_prompt, source_disclaimer, translation_yn, translated_from,
                    original_link, generated_at, generation_model, quality_score, risk_score,
                    status, status_reason
                ) VALUES (
                    :sourceItemId, :contentType, :category, :subcategory, :targetPersona, :language,
                    :title, :writtenContent, :shortSummary, :whyItMatters, :checkNext, :hashtags,
                    :imageUrl, :imagePrompt, :sourceDisclaimer, :translationYn, :translatedFrom,
                    :originalLink, COALESCE(:generatedAt, CURRENT_TIMESTAMP), :generationModel,
                    :qualityScore, :riskScore, :status, :statusReason
                )
                """;
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(sql, params(content), keyHolder, new String[] { "id" });
        Number key = keyHolder.getKey();
        content.setId(key == null ? null : key.longValue());
        return content;
    }

    public Optional<GeneratedContent> findById(Long id) {
        String sql = "SELECT * FROM content.generated_content WHERE id = :id";
        GeneratedContent content = DataAccessUtils.singleResult(
                jdbcTemplate.query(sql, new MapSqlParameterSource("id", id), ContentRowMapper::mapGeneratedContent));
        return Optional.ofNullable(content);
    }

    public Optional<GeneratedContent> findBySourceItemId(Long sourceItemId) {
        String sql = """
                SELECT *
                FROM content.generated_content
                WHERE source_item_id = :sourceItemId
                ORDER BY id DESC
                LIMIT 1
                """;
        GeneratedContent content = DataAccessUtils.singleResult(
                jdbcTemplate.query(sql, new MapSqlParameterSource("sourceItemId", sourceItemId),
                        ContentRowMapper::mapGeneratedContent));
        return Optional.ofNullable(content);
    }

    public List<GeneratedContent> list(String status, String category, int limit, int offset) {
        StringBuilder sql = new StringBuilder("SELECT * FROM content.generated_content WHERE 1 = 1");
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("limit", clampLimit(limit))
                .addValue("offset", Math.max(0, offset));
        if (status != null && !status.isBlank()) {
            sql.append(" AND status = :status");
            params.addValue("status", status);
        }
        if (category != null && !category.isBlank()) {
            sql.append(" AND category = :category");
            params.addValue("category", category);
        }
        sql.append(" ORDER BY generated_at DESC, id DESC LIMIT :limit OFFSET :offset");
        return jdbcTemplate.query(sql.toString(), params, ContentRowMapper::mapGeneratedContent);
    }

    public List<GeneratedContent> findByStatus(String status, int limit) {
        String sql = """
                SELECT *
                FROM content.generated_content
                WHERE status = :status
                ORDER BY generated_at ASC, id ASC
                LIMIT :limit
                """;
        return jdbcTemplate.query(sql, new MapSqlParameterSource()
                .addValue("status", status)
                .addValue("limit", clampLimit(limit)), ContentRowMapper::mapGeneratedContent);
    }

    public void markSentToTelegram(Long id, Long telegramMessageId, String reason) {
        String sql = """
                UPDATE content.generated_content
                SET status = 'SENT_TO_TELEGRAM',
                    telegram_message_id = :telegramMessageId,
                    status_reason = :reason
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("telegramMessageId", telegramMessageId)
                .addValue("reason", defaultString(reason, "")));
    }

    public void fillTelegramMessageId(Long id, Long telegramMessageId) {
        if (telegramMessageId == null) {
            return;
        }
        String sql = """
                UPDATE content.generated_content
                SET telegram_message_id = COALESCE(telegram_message_id, :telegramMessageId)
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("telegramMessageId", telegramMessageId));
    }

    public void updateGeneratedDraft(Long id, GeneratedContent content) {
        String sql = """
                UPDATE content.generated_content
                SET content_type = :contentType,
                    category = :category,
                    subcategory = :subcategory,
                    target_persona = :targetPersona,
                    language = :language,
                    title = :title,
                    written_content = :writtenContent,
                    short_summary = :shortSummary,
                    why_it_matters = :whyItMatters,
                    check_next = :checkNext,
                    hashtags = :hashtags,
                    image_url = :imageUrl,
                    image_prompt = :imagePrompt,
                    source_disclaimer = :sourceDisclaimer,
                    translation_yn = :translationYn,
                    translated_from = :translatedFrom,
                    original_link = :originalLink,
                    generated_at = COALESCE(:generatedAt, CURRENT_TIMESTAMP),
                    generation_model = :generationModel,
                    quality_score = :qualityScore,
                    risk_score = :riskScore,
                    status = 'GENERATED',
                    status_reason = :statusReason
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, params(content).addValue("id", id));
    }

    public void approve(Long id, String reviewerId, String reviewerName, String reason) {
        String sql = """
                UPDATE content.generated_content
                SET status = 'APPROVED',
                    reviewer_id = :reviewerId,
                    reviewer_name = :reviewerName,
                    approved_at = CURRENT_TIMESTAMP,
                    status_reason = :reason
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, reviewerParams(id, reviewerId, reviewerName, reason));
    }

    public void reject(Long id, String reviewerId, String reviewerName, String reason) {
        String sql = """
                UPDATE content.generated_content
                SET status = 'REJECTED',
                    reviewer_id = :reviewerId,
                    reviewer_name = :reviewerName,
                    rejected_at = CURRENT_TIMESTAMP,
                    status_reason = :reason
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, reviewerParams(id, reviewerId, reviewerName, reason));
    }

    public void markEditRequested(Long id, String reviewerId, String reviewerName, String reason) {
        String sql = """
                UPDATE content.generated_content
                SET status = 'GENERATED',
                    reviewer_id = :reviewerId,
                    reviewer_name = :reviewerName,
                    status_reason = :reason
                WHERE id = :id
                """;
        jdbcTemplate.update(sql, reviewerParams(id, reviewerId, reviewerName, reason));
    }

    public Map<String, Long> countByStatus() {
        String sql = "SELECT status, COUNT(*) AS count FROM content.generated_content GROUP BY status";
        Map<String, Long> counts = new LinkedHashMap<>();
        jdbcTemplate.query(sql, rs -> {
            counts.put(rs.getString("status"), rs.getLong("count"));
        });
        return counts;
    }

    private MapSqlParameterSource params(GeneratedContent content) {
        return new MapSqlParameterSource()
                .addValue("sourceItemId", content.getSourceItemId())
                .addValue("contentType", defaultString(content.getContentType(), "NEWS_EXPLAINER"))
                .addValue("category", defaultString(content.getCategory(), ""))
                .addValue("subcategory", defaultString(content.getSubcategory(), ""))
                .addValue("targetPersona", defaultString(content.getTargetPersona(), "foreign workers in Korea"))
                .addValue("language", defaultString(content.getLanguage(), "en"))
                .addValue("title", defaultString(content.getTitle(), "Untitled content"))
                .addValue("writtenContent", defaultString(content.getWrittenContent(), ""))
                .addValue("shortSummary", defaultString(content.getShortSummary(), ""))
                .addValue("whyItMatters", defaultString(content.getWhyItMatters(), ""))
                .addValue("checkNext", defaultString(content.getCheckNext(), ""))
                .addValue("hashtags", defaultString(content.getHashtags(), ""))
                .addValue("imageUrl", defaultString(content.getImageUrl(), ""))
                .addValue("imagePrompt", defaultString(content.getImagePrompt(), ""))
                .addValue("sourceDisclaimer", defaultString(content.getSourceDisclaimer(), ""))
                .addValue("translationYn", Boolean.TRUE.equals(content.getTranslationYn()))
                .addValue("translatedFrom", defaultString(content.getTranslatedFrom(), ""))
                .addValue("originalLink", defaultString(content.getOriginalLink(), ""))
                .addValue("generatedAt", content.getGeneratedAt(), Types.TIMESTAMP_WITH_TIMEZONE)
                .addValue("generationModel", defaultString(content.getGenerationModel(), "rule-based-mvp"))
                .addValue("qualityScore", content.getQualityScore())
                .addValue("riskScore", content.getRiskScore())
                .addValue("status", defaultString(content.getStatus(), "GENERATED"))
                .addValue("statusReason", defaultString(content.getStatusReason(), ""));
    }

    private MapSqlParameterSource reviewerParams(Long id, String reviewerId, String reviewerName, String reason) {
        return new MapSqlParameterSource()
                .addValue("id", id)
                .addValue("reviewerId", defaultString(reviewerId, ""))
                .addValue("reviewerName", defaultString(reviewerName, ""))
                .addValue("reason", defaultString(reason, ""));
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
}
