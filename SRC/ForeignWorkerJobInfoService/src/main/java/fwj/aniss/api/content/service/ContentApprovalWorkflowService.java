package fwj.aniss.api.content.service;

import static fwj.aniss.api.content.model.ContentWorkflowConstants.ACTION_APPROVED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.ACTION_EDIT_REQUESTED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.ACTION_REJECTED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.ACTION_SENT;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.REVIEW_CHANNEL_ADMIN;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.REVIEW_CHANNEL_SCHEDULER;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.REVIEW_CHANNEL_TELEGRAM;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.STATUS_APPROVED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.STATUS_GENERATED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.STATUS_REJECTED;
import static fwj.aniss.api.content.model.ContentWorkflowConstants.STATUS_SENT_TO_TELEGRAM;

import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import fwj.aniss.api.content.collector.CollectionRunService;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ContentDashboardResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.E2eDryRunResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.GenerateContentRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.GeneratedContentResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.PublishTargetResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ReviewActionRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ReviewLogResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SendTelegramRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCatalogResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemInput;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.TelegramCallbackRequest;
import fwj.aniss.api.content.entity.GeneratedContent;
import fwj.aniss.api.content.entity.CommunitySignal;
import fwj.aniss.api.content.entity.ReviewLog;
import fwj.aniss.api.content.entity.SourceItem;
import fwj.aniss.api.content.mapper.ContentApprovalMapper;
import fwj.aniss.api.content.model.ContentWorkflowConstants;
import fwj.aniss.api.content.repository.GeneratedContentRepository;
import fwj.aniss.api.content.repository.CommunitySignalRepository;
import fwj.aniss.api.content.repository.PublishTargetRepository;
import fwj.aniss.api.content.repository.ReviewLogRepository;
import fwj.aniss.api.content.repository.SourceItemRepository;
import fwj.aniss.api.content.telegram.TelegramReviewMessageBuilder;
import fwj.aniss.api.content.telegram.TelegramReviewSender;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ContentApprovalWorkflowService {
    private final SourceItemRepository sourceItemRepository;
    private final GeneratedContentRepository generatedContentRepository;
    private final ReviewLogRepository reviewLogRepository;
    private final PublishTargetRepository publishTargetRepository;
    private final CommunitySignalRepository communitySignalRepository;
    private final ContentApprovalMapper mapper;
    private final TelegramReviewMessageBuilder telegramMessageBuilder;
    private final TelegramReviewSender telegramReviewSender;
    private final SourceCatalogService sourceCatalogService;
    private final CollectionRunService collectionRunService;
    private final DeterministicContentGenerator deterministicContentGenerator;
    private final Environment environment;

    @Value("${content.telegram.review.default-chat-id:}")
    private String defaultReviewChatId;

    @Value("${content.telegram.review.dry-run:true}")
    private boolean defaultTelegramDryRun;

    @Transactional
    public SourceCollectResponse collectSources(SourceCollectRequest request) {
        return collectionRunService.collect(request);
    }

    @Transactional
    public List<GeneratedContentResponse> generateContent(GenerateContentRequest request) {
        List<SourceItem> sourceItems = resolveSourceItems(request);
        List<GeneratedContentResponse> generated = new ArrayList<>();
        for (SourceItem sourceItem : sourceItems) {
            GeneratedContent draft = buildGeneratedContent(sourceItem, request);
            GeneratedContent content = generatedContentRepository.findBySourceItemId(sourceItem.getId())
                    .map(existing -> {
                        if (!List.of(ContentWorkflowConstants.STATUS_COLLECTED, STATUS_GENERATED).contains(existing.getStatus())) {
                            throw new ContentWorkflowException("Content already left generation stage. currentStatus=" + existing.getStatus());
                        }
                        generatedContentRepository.updateGeneratedDraft(existing.getId(), draft);
                        return generatedContentRepository.findById(existing.getId())
                                .orElseThrow(() -> new ContentWorkflowException("Generated content not found after update: " + existing.getId()));
                    })
                    .orElseGet(() -> generatedContentRepository.save(draft));
            publishTargetRepository.upsertPending(content.getId(), "FACEBOOK");
            GeneratedContentResponse response = detail(content.getId());
            generated.add(response);
            if (Boolean.TRUE.equals(request == null ? null : request.sendToTelegram())) {
                sendToTelegram(content.getId(), new SendTelegramRequest(null, request.telegramDryRun(), "generated"));
            }
        }
        return generated;
    }

    @Transactional
    public GeneratedContentResponse sendToTelegram(Long id, SendTelegramRequest request) {
        GeneratedContent content = requireGeneratedContent(id);
        requireStatus(content, STATUS_GENERATED, "Only GENERATED content can be sent to Telegram.");

        boolean dryRun = request == null || request.dryRun() == null ? defaultTelegramDryRun : request.dryRun();
        Long telegramMessageId = null;
        if (!dryRun) {
            String chatId = firstNonBlank(request == null ? null : request.chatId(), defaultReviewChatId);
            telegramMessageId = telegramReviewSender.sendReviewCard(
                    chatId,
                    telegramMessageBuilder.buildMessage(content),
                    telegramMessageBuilder.buildKeyboard(id));
        }

        String reason = dryRun ? "Telegram review dry-run completed." : "Telegram review card sent.";
        generatedContentRepository.markSentToTelegram(id, telegramMessageId, reason);
        reviewLogRepository.save(ReviewLog.builder()
                .generatedContentId(id)
                .reviewChannel(dryRun ? REVIEW_CHANNEL_ADMIN : REVIEW_CHANNEL_TELEGRAM)
                .telegramMessageId(telegramMessageId)
                .reviewerId("")
                .reviewerName("")
                .action(ACTION_SENT)
                .comment(firstNonBlank(request == null ? null : request.comment(), reason))
                .build());
        return detail(id);
    }

    @Transactional
    public GeneratedContentResponse approve(Long id, ReviewActionRequest request, String reviewChannel) {
        GeneratedContent content = requireGeneratedContent(id);
        requireStatus(content, STATUS_SENT_TO_TELEGRAM, "Only SENT_TO_TELEGRAM content can be approved.");
        String reviewerId = firstNonBlank(request == null ? null : request.reviewerId(), "admin");
        String reviewerName = firstNonBlank(request == null ? null : request.reviewerName(), reviewerId);
        String comment = firstNonBlank(request == null ? null : request.comment(), "Approved.");
        generatedContentRepository.approve(id, reviewerId, reviewerName, comment);
        reviewLogRepository.save(ReviewLog.builder()
                .generatedContentId(id)
                .reviewChannel(firstNonBlank(reviewChannel, REVIEW_CHANNEL_ADMIN))
                .telegramMessageId(content.getTelegramMessageId())
                .reviewerId(reviewerId)
                .reviewerName(reviewerName)
                .action(ACTION_APPROVED)
                .comment(comment)
                .build());
        return detail(id);
    }

    @Transactional
    public GeneratedContentResponse reject(Long id, ReviewActionRequest request, String reviewChannel) {
        GeneratedContent content = requireGeneratedContent(id);
        requireStatus(content, STATUS_SENT_TO_TELEGRAM, "Only SENT_TO_TELEGRAM content can be rejected.");
        String reviewerId = firstNonBlank(request == null ? null : request.reviewerId(), "admin");
        String reviewerName = firstNonBlank(request == null ? null : request.reviewerName(), reviewerId);
        String comment = firstNonBlank(request == null ? null : request.comment(), "Rejected.");
        generatedContentRepository.reject(id, reviewerId, reviewerName, comment);
        reviewLogRepository.save(ReviewLog.builder()
                .generatedContentId(id)
                .reviewChannel(firstNonBlank(reviewChannel, REVIEW_CHANNEL_ADMIN))
                .telegramMessageId(content.getTelegramMessageId())
                .reviewerId(reviewerId)
                .reviewerName(reviewerName)
                .action(ACTION_REJECTED)
                .comment(comment)
                .build());
        return detail(id);
    }

    @Transactional
    public GeneratedContentResponse handleTelegramCallback(TelegramCallbackRequest request) {
        TelegramCallbackRequest parsed = normalizeCallback(request);
        if (parsed.telegramMessageId() != null) {
            generatedContentRepository.fillTelegramMessageId(parsed.contentId(), parsed.telegramMessageId());
        }
        if ("APPROVE".equalsIgnoreCase(parsed.action())) {
            return approve(parsed.contentId(), new ReviewActionRequest(
                    parsed.reviewerId(),
                    parsed.reviewerName(),
                    firstNonBlank(parsed.comment(), "Approved from Telegram.")), REVIEW_CHANNEL_TELEGRAM);
        }
        if ("REJECT".equalsIgnoreCase(parsed.action())) {
            return reject(parsed.contentId(), new ReviewActionRequest(
                    parsed.reviewerId(),
                    parsed.reviewerName(),
                    firstNonBlank(parsed.comment(), "Rejected from Telegram.")), REVIEW_CHANNEL_TELEGRAM);
        }
        if ("EDIT_REQUEST".equalsIgnoreCase(parsed.action())) {
            GeneratedContent content = requireGeneratedContent(parsed.contentId());
            requireStatus(content, STATUS_SENT_TO_TELEGRAM, "Only SENT_TO_TELEGRAM content can receive edit requests.");
            generatedContentRepository.markEditRequested(
                    parsed.contentId(),
                    firstNonBlank(parsed.reviewerId(), "telegram"),
                    firstNonBlank(parsed.reviewerName(), "telegram"),
                    firstNonBlank(parsed.comment(), "Edit requested from Telegram."));
            reviewLogRepository.save(ReviewLog.builder()
                    .generatedContentId(parsed.contentId())
                    .reviewChannel(REVIEW_CHANNEL_TELEGRAM)
                    .telegramMessageId(parsed.telegramMessageId())
                    .reviewerId(firstNonBlank(parsed.reviewerId(), "telegram"))
                    .reviewerName(firstNonBlank(parsed.reviewerName(), "telegram"))
                    .action(ACTION_EDIT_REQUESTED)
                    .comment(firstNonBlank(parsed.comment(), "Edit requested from Telegram."))
                    .build());
            return detail(parsed.contentId());
        }
        throw new ContentWorkflowException("Unsupported Telegram callback action: " + parsed.action());
    }

    @Transactional(readOnly = true)
    public List<GeneratedContentResponse> listGenerated(String status, String category, int limit, int offset) {
        return generatedContentRepository.list(status, category, limit, offset)
                .stream()
                .map(mapper::toListResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<SourceItemResponse> listSources(String domain, String category, int limit, int offset) {
        return sourceItemRepository.list(domain, category, limit, offset)
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public GeneratedContentResponse detail(Long id) {
        GeneratedContent content = requireGeneratedContent(id);
        SourceItem sourceItem = content.getSourceItemId() == null
                ? null
                : sourceItemRepository.findById(content.getSourceItemId()).orElse(null);
        return mapper.toResponse(
                content,
                sourceItem,
                reviewLogRepository.listByContentId(id),
                publishTargetRepository.list(id, null, 100));
    }

    @Transactional(readOnly = true)
    public ContentDashboardResponse dashboard() {
        Map<String, Long> counts = new LinkedHashMap<>(generatedContentRepository.countByStatus());
        long total = counts.values().stream().mapToLong(Long::longValue).sum();
        return new ContentDashboardResponse(
                total,
                counts.getOrDefault(ContentWorkflowConstants.STATUS_COLLECTED, 0L),
                counts.getOrDefault(ContentWorkflowConstants.STATUS_GENERATED, 0L),
                counts.getOrDefault(ContentWorkflowConstants.STATUS_SENT_TO_TELEGRAM, 0L),
                counts.getOrDefault(ContentWorkflowConstants.STATUS_APPROVED, 0L),
                counts.getOrDefault(ContentWorkflowConstants.STATUS_REJECTED, 0L),
                counts.getOrDefault(ContentWorkflowConstants.STATUS_PUBLISHED, 0L),
                counts);
    }

    @Transactional(readOnly = true)
    public List<SourceCatalogResponse> sourceCatalog() {
        return sourceCatalogService.list();
    }

    @Transactional(readOnly = true)
    public List<ReviewLogResponse> reviewLogs(Long generatedContentId, int limit) {
        return reviewLogRepository.list(generatedContentId, limit)
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<PublishTargetResponse> publishTargets(Long generatedContentId, String status, int limit) {
        return publishTargetRepository.list(generatedContentId, status, limit)
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public List<CommunitySignalResponse> communitySignals(String category, int limit) {
        return communitySignalRepository.list(category, limit)
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Transactional
    public CommunitySignalResponse saveCommunitySignal(CommunitySignalRequest request) {
        if (request == null || request.topic() == null || request.topic().isBlank()) {
            throw new ContentWorkflowException("Community signal topic is required.");
        }
        CommunitySignal signal = CommunitySignal.builder()
                .sourcePlatform(firstNonBlank(request.sourcePlatform(), "public_community_trend"))
                .sourceUrl(firstNonBlank(request.sourceUrl(), ""))
                .topic(request.topic())
                .language(firstNonBlank(request.language(), "en"))
                .country(firstNonBlank(request.country(), "KR"))
                .category(firstNonBlank(request.category(), "community_signal"))
                .questionPattern(firstNonBlank(request.questionPattern(), ""))
                .frequencyScore(request.frequencyScore() == null ? BigDecimal.ZERO : request.frequencyScore())
                .urgencyScore(request.urgencyScore() == null ? BigDecimal.ZERO : request.urgencyScore())
                .sampleCount(request.sampleCount() == null ? 0 : request.sampleCount())
                .authorHash(firstNonBlank(request.authorHash(), ""))
                .rawRetentionPolicy("ANONYMIZED_SUMMARY_ONLY")
                .piiCheckedYn(Boolean.TRUE.equals(request.piiCheckedYn()))
                .usableForContentYn(Boolean.TRUE.equals(request.usableForContentYn()))
                .termsRiskLevel(firstNonBlank(request.termsRiskLevel(), "UNKNOWN"))
                .build();
        return mapper.toResponse(communitySignalRepository.save(signal));
    }

    public GeneratedContentResponse publishBlocked(Long id) {
        GeneratedContent content = requireGeneratedContent(id);
        if (!STATUS_APPROVED.equals(content.getStatus())) {
            throw new ContentWorkflowException("Only APPROVED content can be considered for publishing. currentStatus=" + content.getStatus());
        }
        throw new ContentWorkflowException("Public publishing is blocked in this phase. Facebook/site auto publish is forbidden.");
    }

    @Transactional
    public E2eDryRunResponse e2eDryRun() {
        if (!localOrDevProfile()) {
            throw new ContentWorkflowException("E2E dry-run API is available only in local/dev profile.");
        }
        String suffix = String.valueOf(System.currentTimeMillis());
        SourceCollectResponse collected = collectSources(new SourceCollectRequest(
                "EMPLOYMENT",
                "manual",
                "employment",
                1,
                false,
                List.of(new SourceItemInput(
                        "EMPLOYMENT",
                        "manual",
                        "E2E Dry Run",
                        "https://local.workconnect/e2e-dry-run/" + suffix,
                        "https://local.workconnect/e2e-dry-run/" + suffix,
                        "https://local.workconnect/e2e-dry-run/" + suffix,
                        "E2E dry-run employment source " + suffix,
                        "Mock source item for verifying COLLECTED to GENERATED to SENT_TO_TELEGRAM dry-run flow.",
                        "Mock source item for verifying the content approval workflow.",
                        "en",
                        "KR",
                        "employment",
                        "e2e",
                        "{\"source\":\"e2e-dry-run\"}",
                        "LOW",
                        "PUBLIC",
                        "LOW",
                        true,
                        true))));
        if (collected.items().isEmpty() || collected.items().get(0).id() == null) {
            throw new ContentWorkflowException("E2E dry-run source item was not created.");
        }
        Long sourceItemId = collected.items().get(0).id();
        List<GeneratedContentResponse> generated = generateContent(new GenerateContentRequest(
                List.of(sourceItemId),
                null,
                "en",
                "foreign workers and residents in Korea",
                false,
                true));
        if (generated.isEmpty()) {
            throw new ContentWorkflowException("E2E dry-run generated content was not created.");
        }
        GeneratedContentResponse sent = sendToTelegram(
                generated.get(0).id(),
                new SendTelegramRequest(null, true, "e2e dry-run"));
        Long reviewLogId = sent.reviewLogs().stream()
                .filter(log -> ACTION_SENT.equals(log.action()))
                .map(ReviewLogResponse::id)
                .findFirst()
                .orElse(null);
        return new E2eDryRunResponse(
                sourceItemId,
                sent.id(),
                sent.status(),
                "Telegram dry-run review log saved; no external message was sent.",
                reviewLogId);
    }

    @Transactional
    public int generatePendingContent(int limit) {
        List<SourceItem> pending = sourceItemRepository.findPendingForGeneration(limit);
        if (pending.isEmpty()) {
            return 0;
        }
        List<Long> ids = pending.stream().map(SourceItem::getId).toList();
        return generateContent(new GenerateContentRequest(ids, null, "en", null, false, true)).size();
    }

    @Transactional
    public SourceCollectResponse runSourceCollection(int limit, boolean dryRun) {
        return collectionRunService.collectAll(limit, dryRun);
    }

    @Transactional
    public int deliverPendingTelegram(int limit) {
        List<GeneratedContent> pending = generatedContentRepository.findByStatus(STATUS_GENERATED, limit);
        int delivered = 0;
        for (GeneratedContent content : pending) {
            sendToTelegram(content.getId(), new SendTelegramRequest(null, true, "scheduler dry-run"));
            delivered += 1;
        }
        return delivered;
    }

    private List<SourceItem> resolveSourceItems(GenerateContentRequest request) {
        List<Long> ids = request == null ? List.of() : nullToEmpty(request.sourceItemIds());
        if (ids.isEmpty()) {
            return sourceItemRepository.findPendingForGeneration(20);
        }
        return ids.stream()
                .map(id -> sourceItemRepository.findById(id)
                        .orElseThrow(() -> new ContentWorkflowException("Source item not found: " + id)))
                .toList();
    }

    private GeneratedContent buildGeneratedContent(SourceItem sourceItem, GenerateContentRequest request) {
        return deterministicContentGenerator.generate(sourceItem, request);
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
                .status(ContentWorkflowConstants.STATUS_COLLECTED)
                .statusReason("Source item collected. Content generation pending.")
                .build();
    }

    private SourceItem toSourceItem(SourceItemInput input, SourceCollectRequest request) {
        String sourceDomain = firstNonBlank(input.sourceDomain(), request == null ? null : request.domain(), "SOCIAL_NEWS");
        String category = firstNonBlank(input.category(), request == null ? null : request.category(), "");
        boolean community = "COMMUNITY".equals(sourceDomain);
        return SourceItem.builder()
                .sourceDomain(sourceDomain)
                .sourcePlatform(firstNonBlank(input.sourcePlatform(), ""))
                .sourceName(firstNonBlank(input.sourceName(), ""))
                .sourceUrl(firstNonBlank(input.sourceUrl(), ""))
                .canonicalUrl(firstNonBlank(input.canonicalUrl(), input.sourceUrl(), ""))
                .publishableLinkUrl(firstNonBlank(input.publishableLinkUrl(), input.canonicalUrl(), input.sourceUrl(), ""))
                .title(firstNonBlank(input.title(), "Untitled source"))
                .bodyText(community ? "" : firstNonBlank(input.bodyText(), ""))
                .summaryText(firstNonBlank(input.summaryText(), ""))
                .language(firstNonBlank(input.language(), "ko"))
                .countryCode(firstNonBlank(input.countryCode(), "KR"))
                .category(category)
                .subcategory(firstNonBlank(input.subcategory(), ""))
                .rawPayload(community ? "{}" : firstNonBlank(input.rawPayload(), "{}"))
                .sourceRiskLevel(firstNonBlank(input.sourceRiskLevel(), "LOW"))
                .accessRestriction(firstNonBlank(input.accessRestriction(), "PUBLIC"))
                .copyrightRiskLevel(firstNonBlank(input.copyrightRiskLevel(), "LOW"))
                .piiCheckedYn(Boolean.TRUE.equals(input.piiCheckedYn()))
                .usableForContentYn(!community && Boolean.TRUE.equals(input.usableForContentYn()))
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

    private TelegramCallbackRequest normalizeCallback(TelegramCallbackRequest request) {
        if (request == null) {
            throw new ContentWorkflowException("Telegram callback request is required.");
        }
        if (request.contentId() != null && request.action() != null) {
            return request;
        }
        String data = request.callbackData();
        if (data == null || data.isBlank()) {
            throw new ContentWorkflowException("Telegram callbackData is required.");
        }
        String[] parts = data.trim().split(":", 3);
        if (parts.length != 3 || !ContentWorkflowConstants.CALLBACK_PREFIX.equals(parts[0])) {
            throw new ContentWorkflowException("Invalid Telegram callbackData: " + data);
        }
        String action = parts[1].trim().toUpperCase();
        if (!List.of("APPROVE", "REJECT", "EDIT_REQUEST").contains(action)) {
            throw new ContentWorkflowException("Unsupported Telegram callback action: " + parts[1]);
        }
        Long contentId;
        try {
            contentId = Long.valueOf(parts[2]);
        } catch (NumberFormatException ex) {
            throw new ContentWorkflowException("Invalid Telegram callback content id: " + parts[2]);
        }
        return new TelegramCallbackRequest(
                contentId,
                action,
                request.reviewerId(),
                request.reviewerName(),
                request.comment(),
                request.telegramMessageId(),
                data);
    }

    private GeneratedContent requireGeneratedContent(Long id) {
        if (id == null) {
            throw new ContentWorkflowException("Generated content id is required.");
        }
        return generatedContentRepository.findById(id)
                .orElseThrow(() -> new ContentWorkflowException("Generated content not found: " + id));
    }

    private void requireStatus(GeneratedContent content, String expected, String message) {
        if (!expected.equals(content.getStatus())) {
            throw new ContentWorkflowException(message + " currentStatus=" + content.getStatus());
        }
    }

    private boolean isCollectable(SourceItemInput input) {
        return input != null && firstNonBlank(input.title(), input.sourceUrl(), input.summaryText()) != null;
    }

    private List<Long> nullToEmpty(List<Long> values) {
        return values == null ? List.of() : values;
    }

    private BigDecimal riskScore(String sourceRiskLevel) {
        return switch (firstNonBlank(sourceRiskLevel, "UNKNOWN")) {
            case "LOW" -> BigDecimal.valueOf(20);
            case "MEDIUM" -> BigDecimal.valueOf(50);
            case "HIGH" -> BigDecimal.valueOf(80);
            default -> BigDecimal.valueOf(60);
        };
    }

    private String whyItMatters(String category, String persona) {
        return "This can help " + persona + " understand practical " + category
                + " information with a source link before taking action.";
    }

    private String defaultHashtags(String category) {
        String normalized = category == null ? "WorkConnectKorea" : category.replaceAll("[^A-Za-z0-9]", "");
        if (normalized.isBlank()) {
            normalized = "WorkConnectKorea";
        }
        return "#WorkConnectKorea #WorkInKorea #" + normalized;
    }

    private boolean localOrDevProfile() {
        String profileValue = environment.getProperty("spring.profile.value", "");
        if ("local".equalsIgnoreCase(profileValue) || "dev".equalsIgnoreCase(profileValue)) {
            return true;
        }
        return Arrays.stream(environment.getActiveProfiles())
                .anyMatch(profile -> "local".equalsIgnoreCase(profile) || "dev".equalsIgnoreCase(profile));
    }

    private String truncate(String value, int maxLength) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.length() <= maxLength ? value : value.substring(0, maxLength) + "...";
    }

    private String firstNonBlank(String... values) {
        if (values == null) {
            return null;
        }
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }
}
