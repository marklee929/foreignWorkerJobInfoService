package fwj.aniss.api.content.collector;

import static fwj.aniss.api.content.model.ContentWorkflowConstants.STATUS_COLLECTED;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemInput;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemResponse;
import fwj.aniss.api.content.entity.CommunitySignal;
import fwj.aniss.api.content.entity.GeneratedContent;
import fwj.aniss.api.content.entity.SourceItem;
import fwj.aniss.api.content.mapper.ContentApprovalMapper;
import fwj.aniss.api.content.repository.CommunitySignalRepository;
import fwj.aniss.api.content.repository.GeneratedContentRepository;
import fwj.aniss.api.content.repository.SourceItemRepository;
import fwj.aniss.api.content.service.ContentWorkflowException;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CollectionRunService {
    private final SourceCollectorRegistry sourceCollectorRegistry;
    private final SourceItemRepository sourceItemRepository;
    private final GeneratedContentRepository generatedContentRepository;
    private final CommunitySignalRepository communitySignalRepository;
    private final ContentApprovalMapper mapper;

    @Transactional
    public SourceCollectResponse collect(SourceCollectRequest request) {
        SourceCollectionResult result = resolveResult(request);
        boolean dryRun = Boolean.TRUE.equals(request == null ? null : request.dryRun());
        List<SourceItemResponse> rows = new ArrayList<>();
        int created = 0;
        int updated = 0;
        int blocked = 0;

        for (SourceItemInput input : result.sourceItems()) {
            if (!isCollectable(input)) {
                blocked += 1;
                continue;
            }
            SourceItem entity = toSourceItem(input, request);
            if (!dryRun) {
                var existing = sourceItemRepository.findByDomainAndUrl(
                        entity.getSourceDomain(),
                        entity.getCanonicalUrl(),
                        entity.getSourceUrl());
                if (existing.isPresent()) {
                    sourceItemRepository.touchLastSeen(existing.get().getId());
                    entity = sourceItemRepository.findById(existing.get().getId()).orElse(existing.get());
                    updated += 1;
                } else {
                    entity = sourceItemRepository.save(entity);
                    generatedContentRepository.save(buildCollectedPlaceholder(entity));
                    created += 1;
                }
            }
            rows.add(mapper.toResponse(entity));
        }

        for (CommunitySignalRequest signalRequest : result.communitySignals()) {
            if (signalRequest == null || isBlank(signalRequest.topic())) {
                blocked += 1;
                continue;
            }
            if (!dryRun) {
                communitySignalRepository.save(toCommunitySignal(signalRequest));
                created += 1;
            }
        }

        return new SourceCollectResponse(
                result.collectedCount(),
                dryRun ? 0 : created,
                dryRun ? 0 : updated,
                blocked,
                dryRun,
                rows);
    }

    @Transactional
    public SourceCollectResponse collectAll(int limit, boolean dryRun) {
        SourceCollectRequest request = new SourceCollectRequest(null, null, null, limit, dryRun, List.of());
        return collect(request);
    }

    private SourceCollectionResult resolveResult(SourceCollectRequest request) {
        List<SourceItemInput> manualItems = request == null || request.items() == null ? List.of() : request.items();
        if (!manualItems.isEmpty()) {
            return SourceCollectionResult.sourceItems(manualItems);
        }

        List<SourceCollector> collectors = sourceCollectorRegistry.matching(request);
        if (collectors.isEmpty()) {
            throw new ContentWorkflowException("No source collector found for request.");
        }
        List<SourceItemInput> sourceItems = new ArrayList<>();
        List<CommunitySignalRequest> communitySignals = new ArrayList<>();
        int blocked = 0;
        for (SourceCollector collector : collectors) {
            try {
                SourceCollectionResult result = collector.collect(request);
                sourceItems.addAll(result.sourceItems());
                communitySignals.addAll(result.communitySignals());
            } catch (RuntimeException ex) {
                blocked += 1;
            }
        }
        if (blocked > 0 && sourceItems.isEmpty() && communitySignals.isEmpty()) {
            throw new ContentWorkflowException("All source collectors failed.");
        }
        return new SourceCollectionResult(sourceItems, communitySignals);
    }

    private SourceItem toSourceItem(SourceItemInput input, SourceCollectRequest request) {
        String sourceDomain = normalizeDomain(firstNonBlank(input.sourceDomain(), request == null ? null : request.domain(), "SOCIAL_NEWS"));
        String sourcePlatform = firstNonBlank(input.sourcePlatform(), request == null ? null : request.sourcePlatform(), "manual");
        String category = firstNonBlank(input.category(), request == null ? null : request.category(), categoryForDomain(sourceDomain));
        String riskLevel = normalizeRisk(firstNonBlank(input.sourceRiskLevel(), riskLevel(sourceDomain, sourcePlatform, category)));
        String copyrightRisk = normalizeRisk(firstNonBlank(input.copyrightRiskLevel(), copyrightRisk(sourceDomain)));
        String accessRestriction = normalizeAccess(firstNonBlank(input.accessRestriction(), "PUBLIC"));
        boolean community = "COMMUNITY".equals(sourceDomain);
        boolean usable = usableForContent(input, sourceDomain, riskLevel, copyrightRisk, accessRestriction);
        String canonicalUrl = firstNonBlank(input.canonicalUrl(), input.sourceUrl(), "");
        String sourceUrl = firstNonBlank(input.sourceUrl(), canonicalUrl, "");

        return SourceItem.builder()
                .sourceDomain(sourceDomain)
                .sourcePlatform(sourcePlatform)
                .sourceName(firstNonBlank(input.sourceName(), sourcePlatform))
                .sourceUrl(sourceUrl)
                .canonicalUrl(canonicalUrl)
                .publishableLinkUrl(firstNonBlank(input.publishableLinkUrl(), canonicalUrl, sourceUrl, ""))
                .title(firstNonBlank(input.title(), "Untitled source"))
                .bodyText(community ? "" : firstNonBlank(input.bodyText(), ""))
                .summaryText(firstNonBlank(input.summaryText(), input.title(), ""))
                .language(firstNonBlank(input.language(), "ko"))
                .countryCode(firstNonBlank(input.countryCode(), "KR"))
                .category(category)
                .subcategory(firstNonBlank(input.subcategory(), ""))
                .collectedAt(OffsetDateTime.now())
                .lastSeenAt(OffsetDateTime.now())
                .sourcePublishedAt(null)
                .rawPayload(community ? "{}" : firstNonBlank(input.rawPayload(), "{}"))
                .sourceRiskLevel(riskLevel)
                .accessRestriction(accessRestriction)
                .copyrightRiskLevel(copyrightRisk)
                .piiCheckedYn(Boolean.TRUE.equals(input.piiCheckedYn()))
                .usableForContentYn(usable)
                .build();
    }

    private CommunitySignal toCommunitySignal(CommunitySignalRequest request) {
        return CommunitySignal.builder()
                .sourcePlatform(firstNonBlank(request.sourcePlatform(), "public_community_trend"))
                .sourceUrl(firstNonBlank(request.sourceUrl(), ""))
                .topic(firstNonBlank(request.topic(), "Untitled topic"))
                .language(firstNonBlank(request.language(), "en"))
                .country(firstNonBlank(request.country(), "KR"))
                .category(firstNonBlank(request.category(), "community_signal"))
                .questionPattern(firstNonBlank(request.questionPattern(), ""))
                .frequencyScore(request.frequencyScore() == null ? BigDecimal.ZERO : request.frequencyScore())
                .urgencyScore(request.urgencyScore() == null ? BigDecimal.ZERO : request.urgencyScore())
                .sampleCount(request.sampleCount() == null ? 0 : request.sampleCount())
                .authorHash(firstNonBlank(request.authorHash(), ""))
                .rawRetentionPolicy("ANONYMIZED_SUMMARY_ONLY")
                .piiCheckedYn(true)
                .usableForContentYn(true)
                .termsRiskLevel(normalizeRisk(firstNonBlank(request.termsRiskLevel(), "UNKNOWN")))
                .build();
    }

    private GeneratedContent buildCollectedPlaceholder(SourceItem sourceItem) {
        return GeneratedContent.builder()
                .sourceItemId(sourceItem.getId())
                .contentType(contentTypeForSource(sourceItem.getSourceDomain()))
                .category(firstNonBlank(sourceItem.getCategory(), "general"))
                .subcategory(firstNonBlank(sourceItem.getSubcategory(), ""))
                .targetPersona("foreign workers and residents in Korea")
                .language("en")
                .title(firstNonBlank(sourceItem.getTitle(), "Untitled source"))
                .writtenContent("")
                .shortSummary(firstNonBlank(sourceItem.getSummaryText(), ""))
                .whyItMatters("")
                .checkNext("")
                .hashtags("")
                .imageUrl("")
                .imagePrompt("")
                .sourceDisclaimer("")
                .translationYn(false)
                .translatedFrom(firstNonBlank(sourceItem.getLanguage(), ""))
                .originalLink(firstNonBlank(sourceItem.getPublishableLinkUrl(), sourceItem.getCanonicalUrl(), sourceItem.getSourceUrl(), ""))
                .generatedAt(OffsetDateTime.now())
                .generationModel("")
                .qualityScore(BigDecimal.ZERO)
                .riskScore(riskScore(sourceItem.getSourceRiskLevel()))
                .status(STATUS_COLLECTED)
                .statusReason("Source item collected. Content generation pending.")
                .build();
    }

    private String contentTypeForSource(String sourceDomain) {
        return switch (firstNonBlank(sourceDomain, "SOCIAL_NEWS")) {
            case "EMPLOYMENT" -> "JOB_GUIDE";
            case "VISA_IMMIGRATION" -> "VISA_GUIDE";
            case "LIVING_INFO" -> "LIVING_TIP";
            case "COMMUNITY" -> "COMMUNITY_FAQ";
            default -> "NEWS_EXPLAINER";
        };
    }

    private BigDecimal riskScore(String sourceRiskLevel) {
        return switch (firstNonBlank(sourceRiskLevel, "UNKNOWN")) {
            case "LOW" -> BigDecimal.valueOf(20);
            case "MEDIUM" -> BigDecimal.valueOf(50);
            case "HIGH" -> BigDecimal.valueOf(80);
            default -> BigDecimal.valueOf(60);
        };
    }

    private boolean usableForContent(
            SourceItemInput input,
            String sourceDomain,
            String riskLevel,
            String copyrightRisk,
            String accessRestriction) {
        if ("COMMUNITY".equals(sourceDomain)) {
            return false;
        }
        if (!"PUBLIC".equals(accessRestriction) || "HIGH".equals(riskLevel) || "HIGH".equals(copyrightRisk)) {
            return false;
        }
        if (input.usableForContentYn() != null) {
            return Boolean.TRUE.equals(input.usableForContentYn());
        }
        return true;
    }

    private String riskLevel(String sourceDomain, String sourcePlatform, String category) {
        if ("COMMUNITY".equals(sourceDomain)) {
            return "HIGH";
        }
        if ("VISA_IMMIGRATION".equals(sourceDomain) || List.of("finance", "healthcare", "housing").contains(category)) {
            return "MEDIUM";
        }
        if (sourcePlatform != null && sourcePlatform.contains("reddit")) {
            return "HIGH";
        }
        return "LOW";
    }

    private String copyrightRisk(String sourceDomain) {
        return "COMMUNITY".equals(sourceDomain) ? "HIGH" : "LOW";
    }

    private String categoryForDomain(String sourceDomain) {
        return switch (sourceDomain) {
            case "EMPLOYMENT" -> "employment";
            case "VISA_IMMIGRATION" -> "visa";
            case "LIVING_INFO" -> "living_info";
            case "COMMUNITY" -> "community_signal";
            default -> "general";
        };
    }

    private String normalizeDomain(String sourceDomain) {
        String normalized = firstNonBlank(sourceDomain, "SOCIAL_NEWS").trim().toUpperCase(Locale.ROOT);
        return switch (normalized) {
            case "EMPLOYMENT", "VISA_IMMIGRATION", "LIVING_INFO", "COMMUNITY", "SOCIAL_NEWS", "OCCUPATION_INFO",
                    "GOVERNMENT_NOTICE" -> normalized;
            default -> "SOCIAL_NEWS";
        };
    }

    private String normalizeRisk(String riskLevel) {
        String normalized = firstNonBlank(riskLevel, "UNKNOWN").trim().toUpperCase(Locale.ROOT);
        return switch (normalized) {
            case "LOW", "MEDIUM", "HIGH", "UNKNOWN" -> normalized;
            default -> "UNKNOWN";
        };
    }

    private String normalizeAccess(String accessRestriction) {
        String normalized = firstNonBlank(accessRestriction, "UNKNOWN").trim().toUpperCase(Locale.ROOT);
        return switch (normalized) {
            case "PUBLIC", "LOGIN_REQUIRED", "PAYWALLED", "PRIVATE", "UNKNOWN" -> normalized;
            default -> "UNKNOWN";
        };
    }

    private boolean isCollectable(SourceItemInput input) {
        return input != null && firstNonBlank(input.title(), input.sourceUrl(), input.summaryText()) != null;
    }

    private boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private String firstNonBlank(String... values) {
        if (values == null) {
            return null;
        }
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value.trim();
            }
        }
        return null;
    }
}
