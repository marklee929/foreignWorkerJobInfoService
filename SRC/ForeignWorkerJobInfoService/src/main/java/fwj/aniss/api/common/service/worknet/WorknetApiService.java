package fwj.aniss.api.common.service.worknet;

import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
import fwj.aniss.api.common.bean.worknet.WorknetJobPost;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;

@Service
public class WorknetApiService {

    private final WebClient webClient;

    @Value("${worknet.api.authkey}")
    private String authKey;

    @Autowired
    public WorknetApiService(WebClient.Builder webClientBuilder, @Value("${worknet.api.url}") String baseUrl) {
        this.webClient = webClientBuilder.baseUrl(baseUrl).build();
    }

    public Mono<WorknetApiResponse> getJobPostings(String keyword) {
        return this.webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .queryParam("authKey", authKey)
                        .queryParam("callTp", "L") // L for List
                        .queryParam("returnType", "JSON")
                        .queryParam("startPage", "1")
                        .queryParam("display", "100")
                        .queryParam("keyword", keyword)
                        .build())
                .retrieve()
                .bodyToMono(WorknetApiResponse.class)
                .onErrorResume(e -> Mono.just(new WorknetApiResponse())); // 에러 발생 시 빈 응답 반환
    }

    public Mono<WorknetApiResponse> getForeignerJobPostings() {
        List<String> keywords = List.of("외국인", "외국인우대", "E-7", "E-9", "D-10", "F-2", "F-4", "F-6");

        return Flux.fromIterable(keywords)
                .flatMap(this::getJobPostings)
                .filter(response -> response.getContent() != null && !response.getContent().isEmpty())
                .flatMap(response -> Flux.fromIterable(response.getContent()))
                .distinct(WorknetJobPost::getWantedAuthNo)
                .collectList()
                .map(jobPosts -> {
                    WorknetApiResponse finalResponse = new WorknetApiResponse();
                    finalResponse.setContent(jobPosts);
                    finalResponse.setTotal(jobPosts.size());
                    return finalResponse;
                });
    }
}