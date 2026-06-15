package fwj.aniss.api.content.dto;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;

public final class ContentWorkflowDto {
    private ContentWorkflowDto() {
    }

    public record SourceCollectRequest(
            String domain,
            String sourcePlatform,
            String category,
            Integer limit,
            Boolean dryRun,
            List<SourceItemInput> items) {
    }

    public record SourceItemInput(
            String sourceDomain,
            String sourcePlatform,
            String sourceName,
            String sourceUrl,
            String canonicalUrl,
            String publishableLinkUrl,
            String title,
            String bodyText,
            String summaryText,
            String language,
            String countryCode,
            String category,
            String subcategory,
            String rawPayload,
            String sourceRiskLevel,
            String accessRestriction,
            String copyrightRiskLevel,
            Boolean piiCheckedYn,
            Boolean usableForContentYn) {
    }

    public record SourceCollectResponse(
            int collected,
            int created,
            int updated,
            int blocked,
            boolean dryRun,
            List<SourceItemResponse> items) {
    }

    public record GenerateContentRequest(
            List<Long> sourceItemIds,
            String contentType,
            String language,
            String targetPersona,
            Boolean sendToTelegram,
            Boolean telegramDryRun) {
    }

    public record SendTelegramRequest(
            String chatId,
            Boolean dryRun,
            String comment) {
    }

    public record ReviewActionRequest(
            String reviewerId,
            String reviewerName,
            String comment) {
    }

    public record TelegramCallbackRequest(
            Long contentId,
            String action,
            String reviewerId,
            String reviewerName,
            String comment,
            Long telegramMessageId,
            String callbackData) {
    }

    public record CommunitySignalRequest(
            String sourcePlatform,
            String sourceUrl,
            String topic,
            String language,
            String country,
            String category,
            String questionPattern,
            BigDecimal frequencyScore,
            BigDecimal urgencyScore,
            Integer sampleCount,
            String authorHash,
            Boolean piiCheckedYn,
            Boolean usableForContentYn,
            String termsRiskLevel) {
    }

    public record SourceCatalogResponse(
            String group,
            String sourceDomain,
            String sourcePlatform,
            String sourceName,
            String category,
            String allowedUse,
            String collectionMode) {
    }

    public record SourceItemResponse(
            Long id,
            String sourceDomain,
            String sourcePlatform,
            String sourceName,
            String sourceUrl,
            String canonicalUrl,
            String publishableLinkUrl,
            String title,
            String bodyText,
            String summaryText,
            String language,
            String countryCode,
            String category,
            String subcategory,
            OffsetDateTime collectedAt,
            OffsetDateTime lastSeenAt,
            OffsetDateTime sourcePublishedAt,
            String rawPayload,
            String sourceRiskLevel,
            String accessRestriction,
            String copyrightRiskLevel,
            Boolean piiCheckedYn,
            Boolean usableForContentYn,
            OffsetDateTime createdAt,
            OffsetDateTime updatedAt) {
    }

    public record GeneratedContentResponse(
            Long id,
            Long sourceItemId,
            String contentType,
            String category,
            String subcategory,
            String targetPersona,
            String language,
            String title,
            String writtenContent,
            String shortSummary,
            String whyItMatters,
            String checkNext,
            String hashtags,
            String imageUrl,
            String imagePrompt,
            String sourceDisclaimer,
            Boolean translationYn,
            String translatedFrom,
            String originalLink,
            OffsetDateTime generatedAt,
            String generationModel,
            BigDecimal qualityScore,
            BigDecimal riskScore,
            String status,
            String statusReason,
            Long telegramMessageId,
            String reviewerId,
            String reviewerName,
            OffsetDateTime approvedAt,
            OffsetDateTime rejectedAt,
            OffsetDateTime publishedAt,
            OffsetDateTime createdAt,
            OffsetDateTime updatedAt,
            SourceItemResponse sourceItem,
            List<ReviewLogResponse> reviewLogs,
            List<PublishTargetResponse> publishTargets) {
    }

    public record ReviewLogResponse(
            Long id,
            Long generatedContentId,
            String reviewChannel,
            Long telegramMessageId,
            String reviewerId,
            String reviewerName,
            String action,
            String comment,
            OffsetDateTime reviewedAt,
            OffsetDateTime createdAt) {
    }

    public record PublishTargetResponse(
            Long id,
            Long generatedContentId,
            String targetChannel,
            String publishStatus,
            String publishedUrl,
            String externalPostId,
            OffsetDateTime publishedAt,
            String errorCategory,
            String errorMessage,
            String requestPayload,
            String responsePayload,
            OffsetDateTime createdAt) {
    }

    public record CommunitySignalResponse(
            Long id,
            String sourcePlatform,
            String sourceUrl,
            String topic,
            String language,
            String country,
            String category,
            String questionPattern,
            BigDecimal frequencyScore,
            BigDecimal urgencyScore,
            Integer sampleCount,
            String authorHash,
            String rawRetentionPolicy,
            Boolean piiCheckedYn,
            Boolean usableForContentYn,
            String termsRiskLevel,
            OffsetDateTime createdAt) {
    }

    public record ContentDashboardResponse(
            long total,
            long collected,
            long generated,
            long sentToTelegram,
            long approved,
            long rejected,
            long published,
            Map<String, Long> statusCounts) {
    }

    public record E2eDryRunResponse(
            Long sourceItemId,
            Long generatedContentId,
            String status,
            String telegramDryRunResult,
            Long reviewLogId) {
    }
}
