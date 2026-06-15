package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class HiKoreaSourceCollector extends AbstractSourceCollector {
    public HiKoreaSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "VISA_IMMIGRATION";
    }

    @Override
    public String sourcePlatform() {
        return "hikorea";
    }

    @Override
    public String sourceName() {
        return "HiKorea";
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
                        "https://www.hikorea.go.kr",
                        "HiKorea immigration service",
                        "Official immigration civil service portal for stay, visa and residence procedures.",
                        "immigration_portal"),
                new OfficialSeed(
                        "https://www.hikorea.go.kr/info/InfoDatail.pt",
                        "HiKorea stay and visa information",
                        "Official HiKorea information pages for stay and visa-related checks.",
                        "visa_notice")));
    }
}
