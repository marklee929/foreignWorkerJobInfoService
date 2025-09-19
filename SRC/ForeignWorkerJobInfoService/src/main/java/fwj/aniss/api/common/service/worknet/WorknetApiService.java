package fwj.aniss.api.common.service.worknet;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
import fwj.aniss.api.common.bean.worknet.WorknetJobPost;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.lang.reflect.Field;
import java.util.List;
import java.util.Optional;

@Slf4j
@Service
public class WorknetApiService {

    private final WebClient webClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${worknet.api.authkey}")
    private String authKey;

    @Autowired
    public WorknetApiService(WebClient.Builder webClientBuilder, @Value("${worknet.api.url}") String baseUrl) {
        this.webClient = webClientBuilder.baseUrl(baseUrl).build();
    }

    public Mono<WorknetApiResponse> getJobPostings(String keyword) {
        if (keyword == null || keyword.isBlank()) {
            return Mono.just(new WorknetApiResponse());
        }
        return this.webClient.get()
                .uri(uriBuilder -> {
                    var ub = uriBuilder
                            .queryParam("authKey", authKey)
                            .queryParam("callTp", "L")
                            .queryParam("returnType", "JSON")
                            .queryParam("startPage", "1")
                            .queryParam("display", "100");
                    if (keyword != null && !keyword.isBlank()) {
                        ub.queryParam("keyword", keyword);
                    }
                    return ub.build();
                })
                .header("Accept", "application/json")
                .retrieve()
                .bodyToMono(String.class)
                .flatMap(body -> {
                    log.info("Worknet RAW response for keyword '{}': {}", keyword, body);
                    try {
                        WorknetApiResponse response = objectMapper.readValue(body, WorknetApiResponse.class);
                        return Mono.just(response);
                    } catch (Exception e) {
                        log.error("Error deserializing Worknet response for keyword '{}'", keyword, e);
                        return Mono.error(e);
                    }
                })
                .onErrorResume(e -> {
                    log.error("Error calling Worknet API for keyword '{}'", keyword, e);
                    return Mono.just(new WorknetApiResponse()); // Return empty response on error
                });
    }

    public Mono<WorknetApiResponse> getForeignerJobPostings(String keyword) {
        List<String> keys = (keyword == null || keyword.isBlank())
                ? List.of("외국인", "외국인우대", "E-7", "E7", "E-9", "E9", "D-10", "F-2", "F-4", "F-6")
                : List.of(keyword, keyword + " 외국인", keyword + " 비자");

        return Flux.fromIterable(keys)
            .flatMap(k -> this.webClient.get().uri(uriBuilder -> uriBuilder
                    .queryParam("authKey", authKey)
                    .queryParam("callTp", "L")
                    .queryParam("returnType", "JSON")
                    .queryParam("startPage", "1")
                    .queryParam("display", "100")
                    .queryParam("keyword", k)
                    .build())
                .header("Accept", "application/json")
                .retrieve()
                .bodyToMono(String.class)
                .flatMap(body -> {
                    log.debug("Raw response for keyword '{}': {}", k, body);
                    try {
                        return Mono.just(objectMapper.readValue(body, WorknetApiResponse.class));
                    } catch (JsonProcessingException e) {
                        log.warn("Could not parse Worknet response as JSON for keyword '{}'. It might be an XML error message. Body: {}", k, body);
                        return Mono.empty(); // XML or other non-JSON response, treat as no data
                    } catch (Exception e) {
                        log.error("Error parsing Worknet response for keyword '{}'", k, e);
                        return Mono.empty();
                    }
                })
                .doOnError(e -> log.error("API call failed for keyword: {}", k, e))
                .onErrorResume(e -> Mono.empty()) // Continue flux even if one call fails
                .map(resp -> Optional.ofNullable(resp.getItems()).orElseGet(List::of)))
            .flatMapIterable(list -> list)
            .distinct(WorknetJobPost::getWantedAuthNo)
            .collectList()
            .map(list -> {
                WorknetApiResponse merged = new WorknetApiResponse();
                try {
                    Field f = WorknetApiResponse.class.getDeclaredField("wanted");
                    f.setAccessible(true);
                    f.set(merged, list);
                    merged.setTotal(list.size());
                } catch (Exception ignore) {
                    log.error("Failed to set 'wanted' field via reflection", ignore);
                }
                return merged;
            });
    }
}