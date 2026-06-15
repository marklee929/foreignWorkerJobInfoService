package fwj.aniss.api.content.collector;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class RedditSourceCollector extends AbstractSourceCollector {
    public RedditSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "COMMUNITY";
    }

    @Override
    public String sourcePlatform() {
        return "reddit";
    }

    @Override
    public String sourceName() {
        return "Reddit";
    }

    @Override
    public String category() {
        return "community_signal";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "HIGH";
    }

    @Override
    public boolean defaultUsableForContent() {
        return false;
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        int limit = limit(request, 3);
        List<CommunitySignalRequest> signals = List.of(
                communitySignal(
                        "https://www.reddit.com/r/korea/",
                        "Questions about work visa eligibility and job-change timing",
                        "Can I change jobs or visa status before my current period ends?",
                        BigDecimal.valueOf(62),
                        BigDecimal.valueOf(78),
                        12),
                communitySignal(
                        "https://www.reddit.com/r/Living_in_Korea/",
                        "Confusion about housing deposits and contract checks",
                        "What should I check before signing a housing contract in Korea?",
                        BigDecimal.valueOf(55),
                        BigDecimal.valueOf(70),
                        9),
                communitySignal(
                        "https://www.reddit.com/r/korea/",
                        "Need for plain-language telecom plan cancellation guidance",
                        "How do I cancel or change a phone plan without unexpected fees?",
                        BigDecimal.valueOf(39),
                        BigDecimal.valueOf(52),
                        7));
        return SourceCollectionResult.communitySignals(signals.stream().limit(limit).toList());
    }
}
