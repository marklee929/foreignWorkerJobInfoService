package fwj.aniss.api.content.collector;

import java.math.BigDecimal;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemInput;

abstract class AbstractSourceCollector implements SourceCollector {
    private static final Pattern TITLE_PATTERN = Pattern.compile("(?is)<title[^>]*>(.*?)</title>");
    private final WebClient webClient;

    protected AbstractSourceCollector(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.build();
    }

    protected SourceCollectionResult collectOfficialPages(SourceCollectRequest request, List<OfficialSeed> seeds) {
        int limit = limit(request, seeds.size());
        boolean dryRun = request != null && Boolean.TRUE.equals(request.dryRun());
        List<SourceItemInput> inputs = new ArrayList<>();
        for (OfficialSeed seed : seeds.stream().limit(limit).toList()) {
            Optional<String> html = dryRun ? Optional.empty() : fetch(seed.url());
            String pageTitle = html.map(this::extractTitle).filter(value -> !value.isBlank()).orElse(seed.title());
            String body = html.map(this::plainText).filter(value -> !value.isBlank()).orElse(seed.summary());
            inputs.add(sourceItem(
                    seed.url(),
                    pageTitle,
                    truncate(body, 1800),
                    truncate(firstNonBlank(seed.summary(), body, pageTitle), 500),
                    seed.subcategory(),
                    rawPayload(seed.url(), dryRun || html.isEmpty())));
        }
        return SourceCollectionResult.sourceItems(inputs);
    }

    protected SourceItemInput sourceItem(
            String url,
            String title,
            String bodyText,
            String summaryText,
            String subcategory,
            String rawPayload) {
        return new SourceItemInput(
                sourceDomain(),
                sourcePlatform(),
                sourceName(),
                firstNonBlank(url, ""),
                firstNonBlank(url, ""),
                firstNonBlank(url, ""),
                firstNonBlank(title, sourceName()),
                firstNonBlank(bodyText, summaryText, ""),
                firstNonBlank(summaryText, bodyText, ""),
                defaultLanguage(),
                "KR",
                category(),
                firstNonBlank(subcategory, ""),
                firstNonBlank(rawPayload, "{}"),
                defaultSourceRiskLevel(),
                "PUBLIC",
                defaultCopyrightRiskLevel(),
                true,
                defaultUsableForContent());
    }

    protected CommunitySignalRequest communitySignal(
            String sourceUrl,
            String topic,
            String questionPattern,
            BigDecimal frequencyScore,
            BigDecimal urgencyScore,
            int sampleCount) {
        return new CommunitySignalRequest(
                sourcePlatform(),
                firstNonBlank(sourceUrl, ""),
                topic,
                "en",
                "KR",
                category(),
                firstNonBlank(questionPattern, ""),
                frequencyScore,
                urgencyScore,
                sampleCount,
                "",
                true,
                true,
                defaultSourceRiskLevel());
    }

    protected int limit(SourceCollectRequest request, int fallback) {
        Integer limit = request == null ? null : request.limit();
        if (limit == null || limit <= 0) {
            return Math.max(1, fallback);
        }
        return Math.min(limit, 100);
    }

    protected String defaultLanguage() {
        return "ko";
    }

    protected String defaultSourceRiskLevel() {
        return "LOW";
    }

    protected String defaultCopyrightRiskLevel() {
        return "LOW";
    }

    protected boolean defaultUsableForContent() {
        return true;
    }

    protected String rawPayload(String seedUrl, boolean fallback) {
        return "{\"collector\":\"" + escapeJson(sourcePlatform())
                + "\",\"seedUrl\":\"" + escapeJson(seedUrl)
                + "\",\"fallback\":" + fallback + "}";
    }

    protected String firstNonBlank(String... values) {
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

    protected String truncate(String value, int maxLength) {
        if (value == null || value.isBlank()) {
            return "";
        }
        String normalized = value.replaceAll("\\s+", " ").trim();
        return normalized.length() <= maxLength ? normalized : normalized.substring(0, maxLength) + "...";
    }

    private Optional<String> fetch(String url) {
        try {
            String body = webClient.get()
                    .uri(url)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(8))
                    .block();
            return Optional.ofNullable(body);
        } catch (RuntimeException ex) {
            return Optional.empty();
        }
    }

    private String extractTitle(String html) {
        Matcher matcher = TITLE_PATTERN.matcher(html == null ? "" : html);
        if (!matcher.find()) {
            return "";
        }
        return plainText(matcher.group(1));
    }

    private String plainText(String html) {
        if (html == null || html.isBlank()) {
            return "";
        }
        return html.replaceAll("(?is)<script.*?</script>", " ")
                .replaceAll("(?is)<style.*?</style>", " ")
                .replaceAll("(?s)<[^>]+>", " ")
                .replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", "\"")
                .replace("&#39;", "'")
                .replaceAll("\\s+", " ")
                .trim();
    }

    private String escapeJson(String value) {
        return value == null ? "" : value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    protected record OfficialSeed(String url, String title, String summary, String subcategory) {
    }
}
