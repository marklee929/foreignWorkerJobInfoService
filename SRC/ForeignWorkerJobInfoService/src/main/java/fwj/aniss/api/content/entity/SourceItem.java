package fwj.aniss.api.content.entity;

import java.time.OffsetDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SourceItem {
    private Long id;
    private String sourceDomain;
    private String sourcePlatform;
    private String sourceName;
    private String sourceUrl;
    private String canonicalUrl;
    private String publishableLinkUrl;
    private String title;
    private String bodyText;
    private String summaryText;
    private String language;
    private String countryCode;
    private String category;
    private String subcategory;
    private OffsetDateTime collectedAt;
    private OffsetDateTime lastSeenAt;
    private OffsetDateTime sourcePublishedAt;
    private String rawPayload;
    private String sourceRiskLevel;
    private String accessRestriction;
    private String copyrightRiskLevel;
    private Boolean piiCheckedYn;
    private Boolean usableForContentYn;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}
