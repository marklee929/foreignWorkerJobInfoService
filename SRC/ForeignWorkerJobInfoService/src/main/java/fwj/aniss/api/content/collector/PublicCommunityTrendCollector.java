package fwj.aniss.api.content.collector;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class PublicCommunityTrendCollector extends AbstractSourceCollector {
    public PublicCommunityTrendCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "COMMUNITY";
    }

    @Override
    public String sourcePlatform() {
        return "public_community_trend";
    }

    @Override
    public String sourceName() {
        return "Public Community Trend";
    }

    @Override
    public String category() {
        return "community_signal";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "MEDIUM";
    }

    @Override
    public boolean defaultUsableForContent() {
        return false;
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        int limit = limit(request, 4);
        List<CommunitySignalRequest> signals = List.of(
                communitySignal(
                        "",
                        "Repeated questions about finding foreigner-friendly employers",
                        "Where can I find companies that understand visa restrictions?",
                        BigDecimal.valueOf(74),
                        BigDecimal.valueOf(66),
                        18),
                communitySignal(
                        "",
                        "Need for checklist content before visiting immigration offices",
                        "What documents should I prepare before going to immigration?",
                        BigDecimal.valueOf(68),
                        BigDecimal.valueOf(81),
                        16),
                communitySignal(
                        "",
                        "Healthcare registration and insurance billing uncertainty",
                        "How do I check whether I am registered for national health insurance?",
                        BigDecimal.valueOf(46),
                        BigDecimal.valueOf(63),
                        8),
                communitySignal(
                        "",
                        "Bank account opening questions after arrival in Korea",
                        "What documents are commonly needed to open a bank account?",
                        BigDecimal.valueOf(43),
                        BigDecimal.valueOf(50),
                        7));
        return SourceCollectionResult.communitySignals(signals.stream().limit(limit).toList());
    }
}
