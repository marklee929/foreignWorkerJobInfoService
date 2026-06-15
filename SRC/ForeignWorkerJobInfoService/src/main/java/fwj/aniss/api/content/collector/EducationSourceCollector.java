package fwj.aniss.api.content.collector;

import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class EducationSourceCollector extends AbstractSourceCollector {
    public EducationSourceCollector(WebClient.Builder webClientBuilder) {
        super(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "LIVING_INFO";
    }

    @Override
    public String sourcePlatform() {
        return "education";
    }

    @Override
    public String sourceName() {
        return "Education";
    }

    @Override
    public String category() {
        return "education";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        return collectOfficialPages(request, List.of(
                new OfficialSeed(
                        "https://www.studyinkorea.go.kr",
                        "Study in Korea education information",
                        "Education and study information for international residents and students in Korea.",
                        "study_in_korea"),
                new OfficialSeed(
                        "https://www.moe.go.kr",
                        "Ministry of Education information",
                        "Official Ministry of Education information and public notices.",
                        "education_notice")));
    }
}
