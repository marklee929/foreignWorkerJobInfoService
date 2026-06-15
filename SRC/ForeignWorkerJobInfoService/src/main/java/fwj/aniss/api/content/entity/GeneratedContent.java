package fwj.aniss.api.content.entity;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GeneratedContent {
    private Long id;
    private Long sourceItemId;
    private String contentType;
    private String category;
    private String subcategory;
    private String targetPersona;
    private String language;
    private String title;
    private String writtenContent;
    private String shortSummary;
    private String whyItMatters;
    private String checkNext;
    private String hashtags;
    private String imageUrl;
    private String imagePrompt;
    private String sourceDisclaimer;
    private Boolean translationYn;
    private String translatedFrom;
    private String originalLink;
    private OffsetDateTime generatedAt;
    private String generationModel;
    private BigDecimal qualityScore;
    private BigDecimal riskScore;
    private String status;
    private String statusReason;
    private Long telegramMessageId;
    private String reviewerId;
    private String reviewerName;
    private OffsetDateTime approvedAt;
    private OffsetDateTime rejectedAt;
    private OffsetDateTime publishedAt;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
