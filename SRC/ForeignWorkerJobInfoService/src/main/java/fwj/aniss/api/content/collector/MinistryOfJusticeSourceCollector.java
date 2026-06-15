package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class MinistryOfJusticeSourceCollector extends AbstractSourceCollector {
    public MinistryOfJusticeSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "VISA_IMMIGRATION";
    }

    @Override
    public String sourcePlatform() {
        return "moj";
    }

    @Override
    public String sourceName() {
        return "Ministry of Justice";
    }

    @Override
    public String category() {
        return "visa";
    }

    @Override
    public String defaultSourceRiskLevel() {
        return "MEDIUM";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.moj.go.kr",
                        "Ministry of Justice immigration policy",
                        "Official Ministry of Justice information for immigration and foreigner policy.",
                        "official_policy"),
                new OfficialSeed(
                        "https://www.immigration.go.kr",
                        "Korea Immigration Service",
                        "Official Korea Immigration Service notices and immigration information.",
                        "immigration_notice")));
    }
}
