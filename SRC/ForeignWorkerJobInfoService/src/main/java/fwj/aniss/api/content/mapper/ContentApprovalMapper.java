package fwj.aniss.api.content.mapper;

import java.util.List;

import org.springframework.stereotype.Component;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.GeneratedContentResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.PublishTargetResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ReviewLogResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemResponse;
import fwj.aniss.api.content.entity.CommunitySignal;
import fwj.aniss.api.content.entity.GeneratedContent;
import fwj.aniss.api.content.entity.PublishTarget;
import fwj.aniss.api.content.entity.ReviewLog;
import fwj.aniss.api.content.entity.SourceItem;

@Component
public class ContentApprovalMapper {
    public SourceItemResponse toResponse(SourceItem item) {
        if (item == null) {
            return null;
        }
        return new SourceItemResponse(
                item.getId(),
                item.getSourceDomain(),
                item.getSourcePlatform(),
                item.getSourceName(),
                item.getSourceUrl(),
                item.getCanonicalUrl(),
                item.getPublishableLinkUrl(),
                item.getTitle(),
                item.getBodyText(),
                item.getSummaryText(),
                item.getLanguage(),
                item.getCountryCode(),
                item.getCategory(),
                item.getSubcategory(),
                item.getCollectedAt(),
                item.getLastSeenAt(),
                item.getSourcePublishedAt(),
                item.getRawPayload(),
                item.getSourceRiskLevel(),
                item.getAccessRestriction(),
                item.getCopyrightRiskLevel(),
                item.getPiiCheckedYn(),
                item.getUsableForContentYn(),
                item.getCreatedAt(),
                item.getUpdatedAt());
    }

    public GeneratedContentResponse toResponse(
            GeneratedContent content,
            SourceItem sourceItem,
            List<ReviewLog> reviewLogs,
            List<PublishTarget> publishTargets) {
        return new GeneratedContentResponse(
                content.getId(),
                content.getSourceItemId(),
                content.getContentType(),
                content.getCategory(),
                content.getSubcategory(),
                content.getTargetPersona(),
                content.getLanguage(),
                content.getTitle(),
                content.getWrittenContent(),
                content.getShortSummary(),
                content.getWhyItMatters(),
                content.getCheckNext(),
                content.getHashtags(),
                content.getImageUrl(),
                content.getImagePrompt(),
                content.getSourceDisclaimer(),
                content.getTranslationYn(),
                content.getTranslatedFrom(),
                content.getOriginalLink(),
                content.getGeneratedAt(),
                content.getGenerationModel(),
                content.getQualityScore(),
                content.getRiskScore(),
                content.getStatus(),
                content.getStatusReason(),
                content.getTelegramMessageId(),
                content.getReviewerId(),
                content.getReviewerName(),
                content.getApprovedAt(),
                content.getRejectedAt(),
                content.getPublishedAt(),
                content.getCreatedAt(),
                content.getUpdatedAt(),
                toResponse(sourceItem),
                reviewLogs.stream().map(this::toResponse).toList(),
                publishTargets.stream().map(this::toResponse).toList());
    }

    public GeneratedContentResponse toListResponse(GeneratedContent content) {
        return toResponse(content, null, List.of(), List.of());
    }

    public ReviewLogResponse toResponse(ReviewLog log) {
        return new ReviewLogResponse(
                log.getId(),
                log.getGeneratedContentId(),
                log.getReviewChannel(),
                log.getTelegramMessageId(),
                log.getReviewerId(),
                log.getReviewerName(),
                log.getAction(),
                log.getComment(),
                log.getReviewedAt(),
                log.getCreatedAt());
    }

    public PublishTargetResponse toResponse(PublishTarget target) {
        return new PublishTargetResponse(
                target.getId(),
                target.getGeneratedContentId(),
                target.getTargetChannel(),
                target.getPublishStatus(),
                target.getPublishedUrl(),
                target.getExternalPostId(),
                target.getPublishedAt(),
                target.getErrorCategory(),
                target.getErrorMessage(),
                target.getRequestPayload(),
                target.getResponsePayload(),
                target.getCreatedAt());
    }

    public CommunitySignalResponse toResponse(CommunitySignal signal) {
        return new CommunitySignalResponse(
                signal.getId(),
                signal.getSourcePlatform(),
                signal.getSourceUrl(),
                signal.getTopic(),
                signal.getLanguage(),
                signal.getCountry(),
                signal.getCategory(),
                signal.getQuestionPattern(),
                signal.getFrequencyScore(),
                signal.getUrgencyScore(),
                signal.getSampleCount(),
                signal.getAuthorHash(),
                signal.getRawRetentionPolicy(),
                signal.getPiiCheckedYn(),
                signal.getUsableForContentYn(),
                signal.getTermsRiskLevel(),
                signal.getCreatedAt());
    }
}
