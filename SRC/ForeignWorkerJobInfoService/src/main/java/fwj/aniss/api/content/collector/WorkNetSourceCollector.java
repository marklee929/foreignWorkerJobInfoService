package fwj.aniss.api.content.collector;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import fwj.aniss.api.common.bean.worknet.WorknetJobPost;
import fwj.aniss.api.common.service.worknet.WorknetApiService;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemInput;

@Component
public class WorkNetSourceCollector implements SourceCollector {
    private final WorknetApiService worknetApiService;
    private final WorkNetFallback fallback;

    public WorkNetSourceCollector(WorknetApiService worknetApiService, WebClient.Builder webClientBuilder) {
        this.worknetApiService = worknetApiService;
        this.fallback = new WorkNetFallback(webClientBuilder);
    }

    @Override
    public String sourceDomain() {
        return "EMPLOYMENT";
    }

    @Override
    public String sourcePlatform() {
        return "worknet";
    }

    @Override
    public String sourceName() {
        return "WorkNet";
    }

    @Override
    public String category() {
        return "employment";
    }

    @Override
    public SourceCollectionResult collect(SourceCollectRequest request) {
        if (request != null && Boolean.TRUE.equals(request.dryRun())) {
            return fallback.collect(request);
        }
        try {
            List<WorknetJobPost> posts = worknetApiService.getForeignerJobPostings(null)
                    .map(response -> response.getWanted() == null ? List.<WorknetJobPost>of() : response.getWanted())
                    .block(java.time.Duration.ofSeconds(12));
            if (posts == null || posts.isEmpty()) {
                return fallback.collect(request);
            }
            int limit = fallback.limit(request, posts.size());
            List<SourceItemInput> items = new ArrayList<>();
            for (WorknetJobPost post : posts.stream().limit(limit).toList()) {
                String url = fallback.firstNonBlank(post.getWantedInfoUrl(), post.getWantedMobileInfoUrl(), "https://www.work24.go.kr");
                String summary = "Company: " + fallback.firstNonBlank(post.getCompany(), "-")
                        + "\nRegion: " + fallback.firstNonBlank(post.getRegion(), "-")
                        + "\nSalary: " + fallback.firstNonBlank(post.getSalTpNm(), "") + " " + fallback.firstNonBlank(post.getSal(), "")
                        + "\nClose date: " + fallback.firstNonBlank(post.getCloseDt(), "-");
                items.add(fallback.sourceItem(
                        url,
                        fallback.firstNonBlank(post.getTitle(), "WorkNet job posting"),
                        summary,
                        summary,
                        "job_posting",
                        fallback.rawPayload(url, false)));
            }
            return SourceCollectionResult.sourceItems(items);
        } catch (RuntimeException ex) {
            return fallback.collect(request);
        }
    }

    static class WorkNetFallback extends AbstractSourceCollector {
        WorkNetFallback(WebClient.Builder webClientBuilder) {
            super(webClientBuilder);
        }

        @Override
        public String sourceDomain() {
            return "EMPLOYMENT";
        }

        @Override
        public String sourcePlatform() {
            return "worknet";
        }

        @Override
        public String sourceName() {
            return "WorkNet";
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
                            "WorkNet foreign-worker friendly job discovery",
                            "Fallback collector item for WorkNet job information when the public API is unavailable.",
                            "api_fallback"),
                    new OfficialSeed(
                            "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do",
                            "WorkNet open API job information",
                            "WorkNet open API endpoint for employment posting discovery.",
                            "open_api")));
        }
    }
}
