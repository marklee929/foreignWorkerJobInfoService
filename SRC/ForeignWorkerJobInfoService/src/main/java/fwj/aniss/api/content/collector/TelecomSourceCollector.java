package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class TelecomSourceCollector extends AbstractSourceCollector {
    public TelecomSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "LIVING_INFO";
    }

    @Override
    public String sourcePlatform() {
        return "telecom";
    }

    @Override
    public String sourceName() {
        return "Telecom";
    }

    @Override
    public String category() {
        return "telecom";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.wiseuser.go.kr",
                        "Wiseuser telecom consumer information",
                        "Telecom consumer information for mobile contracts, fees and user protection checks.",
                        "telecom_consumer"),
                new OfficialSeed(
                        "https://www.kcc.go.kr",
                        "Korea Communications Commission notices",
                        "Official communications policy and user protection information.",
                        "communications_notice")));
    }
}
