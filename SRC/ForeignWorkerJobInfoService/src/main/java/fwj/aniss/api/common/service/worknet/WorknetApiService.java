package fwj.aniss.api.common.service.worknet;

import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

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
                .bodyToMono(WorknetApiResponse.class);
    }

    public Mono<WorknetApiResponse> getForeignerJobPostings(String keyword) {
        String searchKeyword = (keyword == null || keyword.isBlank()) ? "f2" : keyword + " f2";
        return this.webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .queryParam("authKey", authKey)
                        .queryParam("callTp", "L") // L for List
                        .queryParam("returnType", "JSON")
                        .queryParam("startPage", "1")
                        .queryParam("display", "100")
                        .queryParam("keyword", searchKeyword)
                        .build())
                .retrieve()
                .bodyToMono(WorknetApiResponse.class);
    }
}
