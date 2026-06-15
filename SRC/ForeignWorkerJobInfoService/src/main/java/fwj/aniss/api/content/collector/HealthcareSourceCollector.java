package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class HealthcareSourceCollector extends AbstractSourceCollector {
    public HealthcareSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "LIVING_INFO";
    }

    @Override
    public String sourcePlatform() {
        return "healthcare";
    }

    @Override
    public String sourceName() {
        return "Healthcare";
    }

    @Override
    public String category() {
        return "healthcare";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "MEDIUM";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.nhis.or.kr",
                        "National Health Insurance Service information",
                        "Official health insurance information for checking eligibility, insurance services and notices.",
                        "health_insurance"),
                new OfficialSeed(
                        "https://www.mohw.go.kr",
                        "Ministry of Health and Welfare information",
                        "Official health and welfare information relevant to residents in Korea.",
                        "health_welfare")));
    }
}
