package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class FinanceSourceCollector extends AbstractSourceCollector {
    public FinanceSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "LIVING_INFO";
    }

    @Override
    public String sourcePlatform() {
        return "finance";
    }

    @Override
    public String sourceName() {
        return "Finance";
    }

    @Override
    public String category() {
        return "finance";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "MEDIUM";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.fss.or.kr",
                        "Financial Supervisory Service consumer information",
                        "Public financial consumer information for checking safe banking, fraud prevention and financial notices.",
                        "consumer_finance"),
                new OfficialSeed(
                        "https://www.fine.fss.or.kr",
                        "FINE financial information portal",
                        "Financial information portal for consumer-facing financial checks and official guidance.",
                        "financial_guidance")));
    }
}
