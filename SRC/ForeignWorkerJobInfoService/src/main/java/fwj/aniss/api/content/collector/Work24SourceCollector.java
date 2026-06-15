package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class Work24SourceCollector extends AbstractSourceCollector {
    public Work24SourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "EMPLOYMENT";
    }

    @Override
    public String sourcePlatform() {
        return "work24";
    }

    @Override
    public String sourceName() {
        return "Work24";
    }

    @Override
    public String category() {
        return "employment";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.work24.go.kr",
                        "Work24 employment information",
                        "Official Work24 employment service information for job seekers in Korea.",
                        "official_job_portal"),
                new OfficialSeed(
                        "https://www.work24.go.kr/cm/main.do",
                        "Work24 job seeker services",
                        "Work24 provides job search, employment support and labor market information.",
                        "employment_support")));
    }
}
