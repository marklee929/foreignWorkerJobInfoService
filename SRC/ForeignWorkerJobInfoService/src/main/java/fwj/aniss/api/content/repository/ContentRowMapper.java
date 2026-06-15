package fwj.aniss.api.content.repository;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;

import fwj.aniss.api.content.entity.CommunitySignal;
import fwj.aniss.api.content.entity.GeneratedContent;
import fwj.aniss.api.content.entity.PublishTarget;
import fwj.aniss.api.content.entity.ReviewLog;
import fwj.aniss.api.content.entity.SourceItem;

final class ContentRowMapper {
    private ContentRowMapper() {
    }

    static SourceItem mapSourceItem(ResultSet rs, int rowNum) throws SQLException {
        return SourceItem.builder()
                .id(rs.getLong("id"))
                .sourceDomain(rs.getString("source_domain"))
                .sourcePlatform(rs.getString("source_platform"))
                .sourceName(rs.getString("source_name"))
                .sourceUrl(rs.getString("source_url"))
                .canonicalUrl(rs.getString("canonical_url"))
                .publishableLinkUrl(rs.getString("publishable_link_url"))
                .title(rs.getString("title"))
                .bodyText(rs.getString("body_text"))
                .summaryText(rs.getString("summary_text"))
                .language(rs.getString("language"))
                .countryCode(rs.getString("country_code"))
                .category(rs.getString("category"))
                .subcategory(rs.getString("subcategory"))
                .collectedAt(offsetDateTime(rs, "collected_at"))
                .lastSeenAt(offsetDateTime(rs, "last_seen_at"))
                .sourcePublishedAt(offsetDateTime(rs, "source_published_at"))
                .rawPayload(rs.getString("raw_payload"))
                .sourceRiskLevel(rs.getString("source_risk_level"))
                .accessRestriction(rs.getString("access_restriction"))
                .copyrightRiskLevel(rs.getString("copyright_risk_level"))
                .piiCheckedYn(rs.getBoolean("pii_checked_yn"))
                .usableForContentYn(rs.getBoolean("usable_for_content_yn"))
                .createdAt(offsetDateTime(rs, "created_at"))
                .updatedAt(offsetDateTime(rs, "updated_at"))
                .build();
    }

    static GeneratedContent mapGeneratedContent(ResultSet rs, int rowNum) throws SQLException {
        Long telegramMessageId = longOrNull(rs, "telegram_message_id");
        return GeneratedContent.builder()
                .id(rs.getLong("id"))
                .sourceItemId(longOrNull(rs, "source_item_id"))
                .contentType(rs.getString("content_type"))
                .category(rs.getString("category"))
                .subcategory(rs.getString("subcategory"))
                .targetPersona(rs.getString("target_persona"))
                .language(rs.getString("language"))
                .title(rs.getString("title"))
                .writtenContent(rs.getString("written_content"))
                .shortSummary(rs.getString("short_summary"))
                .whyItMatters(rs.getString("why_it_matters"))
                .checkNext(rs.getString("check_next"))
                .hashtags(rs.getString("hashtags"))
                .imageUrl(rs.getString("image_url"))
                .imagePrompt(rs.getString("image_prompt"))
                .sourceDisclaimer(rs.getString("source_disclaimer"))
                .translationYn(rs.getBoolean("translation_yn"))
                .translatedFrom(rs.getString("translated_from"))
                .originalLink(rs.getString("original_link"))
                .generatedAt(offsetDateTime(rs, "generated_at"))
                .generationModel(rs.getString("generation_model"))
                .qualityScore(rs.getBigDecimal("quality_score"))
                .riskScore(rs.getBigDecimal("risk_score"))
                .status(rs.getString("status"))
                .statusReason(rs.getString("status_reason"))
                .telegramMessageId(telegramMessageId)
                .reviewerId(rs.getString("reviewer_id"))
                .reviewerName(rs.getString("reviewer_name"))
                .approvedAt(offsetDateTime(rs, "approved_at"))
                .rejectedAt(offsetDateTime(rs, "rejected_at"))
                .publishedAt(offsetDateTime(rs, "published_at"))
                .createdAt(offsetDateTime(rs, "created_at"))
                .updatedAt(offsetDateTime(rs, "updated_at"))
                .build();
    }

    static ReviewLog mapReviewLog(ResultSet rs, int rowNum) throws SQLException {
        return ReviewLog.builder()
                .id(rs.getLong("id"))
                .generatedContentId(rs.getLong("generated_content_id"))
                .reviewChannel(rs.getString("review_channel"))
                .telegramMessageId(longOrNull(rs, "telegram_message_id"))
                .reviewerId(rs.getString("reviewer_id"))
                .reviewerName(rs.getString("reviewer_name"))
                .action(rs.getString("action"))
                .comment(rs.getString("comment"))
                .reviewedAt(offsetDateTime(rs, "reviewed_at"))
                .createdAt(offsetDateTime(rs, "created_at"))
                .build();
    }

    static PublishTarget mapPublishTarget(ResultSet rs, int rowNum) throws SQLException {
        return PublishTarget.builder()
                .id(rs.getLong("id"))
                .generatedContentId(rs.getLong("generated_content_id"))
                .targetChannel(rs.getString("target_channel"))
                .publishStatus(rs.getString("publish_status"))
                .publishedUrl(rs.getString("published_url"))
                .externalPostId(rs.getString("external_post_id"))
                .publishedAt(offsetDateTime(rs, "published_at"))
                .errorCategory(rs.getString("error_category"))
                .errorMessage(rs.getString("error_message"))
                .requestPayload(rs.getString("request_payload"))
                .responsePayload(rs.getString("response_payload"))
                .createdAt(offsetDateTime(rs, "created_at"))
                .build();
    }

    static CommunitySignal mapCommunitySignal(ResultSet rs, int rowNum) throws SQLException {
        return CommunitySignal.builder()
                .id(rs.getLong("id"))
                .sourcePlatform(rs.getString("source_platform"))
                .sourceUrl(rs.getString("source_url"))
                .topic(rs.getString("topic"))
                .language(rs.getString("language"))
                .country(rs.getString("country"))
                .category(rs.getString("category"))
                .questionPattern(rs.getString("question_pattern"))
                .frequencyScore(rs.getBigDecimal("frequency_score"))
                .urgencyScore(rs.getBigDecimal("urgency_score"))
                .sampleCount(rs.getInt("sample_count"))
                .authorHash(rs.getString("author_hash"))
                .rawRetentionPolicy(rs.getString("raw_retention_policy"))
                .piiCheckedYn(rs.getBoolean("pii_checked_yn"))
                .usableForContentYn(rs.getBoolean("usable_for_content_yn"))
                .termsRiskLevel(rs.getString("terms_risk_level"))
                .createdAt(offsetDateTime(rs, "created_at"))
                .build();
    }

    private static OffsetDateTime offsetDateTime(ResultSet rs, String column) throws SQLException {
        return rs.getObject(column, OffsetDateTime.class);
    }

    private static Long longOrNull(ResultSet rs, String column) throws SQLException {
        long value = rs.getLong(column);
        return rs.wasNull() ? null : value;
    }
}
