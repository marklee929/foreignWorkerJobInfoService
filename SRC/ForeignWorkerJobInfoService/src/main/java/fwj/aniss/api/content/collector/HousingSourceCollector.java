package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class HousingSourceCollector extends AbstractSourceCollector {
    public HousingSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "LIVING_INFO";
    }

    @Override
    public String sourcePlatform() {
        return "housing";
    }

    @Override
    public String sourceName() {
        return "Housing";
    }

    @Override
    public String category() {
        return "housing";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "MEDIUM";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.myhome.go.kr",
                        "Housing support information",
                        "Public housing information that can help residents check rental, support and housing policy links.",
                        "housing_support"),
                new OfficialSeed(
                        "https://www.gov.kr",
                        "Government housing civil services",
                        "Government service portal entry point for public housing and civil service information.",
                        "government_service")));
    }
}
