package fwj.aniss.api.common.service.worknet;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import fwj.aniss.api.common.bean.worknet.WorknetApiRequest;
import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
import fwj.aniss.api.common.bean.worknet.WorknetJobPost;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
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
    private final XmlMapper xmlMapper = new XmlMapper();

    @Value("${worknet.api.authkey}")
    private String authKey;

    @Autowired
    public WorknetApiService(WebClient.Builder webClientBuilder, @Value("${worknet.api.url}") String baseUrl) {
        this.webClient = webClientBuilder.baseUrl(baseUrl).build();
        this.xmlMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }

    public Mono<WorknetApiResponse> getJobPostings(WorknetApiRequest request) {
        log.info("Calling Worknet API with request: {}", request);

        return this.webClient.get()
                .uri(uriBuilder -> uriBuilder.queryParams(toMultiValueMap(request)).build())
                .retrieve()
                .bodyToMono(String.class)
                .flatMap(body -> {
                    log.debug("Worknet RAW response for keyword '{}': {}", request.getKeyword(), body);
                    try {
                        return Mono.just(xmlMapper.readValue(body, WorknetApiResponse.class));
                    } catch (JsonProcessingException e) {
                        log.error("Error deserializing Worknet response for keyword '{}'", request.getKeyword(), e);
                        return Mono.error(e);
                    }
                })
                .doOnNext(response -> {
                    if (response.getError() != null) {
                        log.warn("Worknet API error for keyword '{}': {}", request.getKeyword(), response.getError());
                    }
                })
                .onErrorResume(e -> {
                    log.error("Error calling Worknet API for keyword '{}'", request.getKeyword(), e);
                    return Mono.just(new WorknetApiResponse()); // Return empty response on error
                });
    }

    private MultiValueMap<String, String> toMultiValueMap(WorknetApiRequest request) {
        MultiValueMap<String, String> map = new LinkedMultiValueMap<>();
        map.add("authKey", authKey); // Use authKey from properties
        map.add("callTp", request.getCallTp());
        map.add("returnType", request.getReturnType());
        map.add("startPage", String.valueOf(request.getStartPage()));
        map.add("display", String.valueOf(request.getDisplay()));

        if (request.getRegion() != null) map.add("region", request.getRegion());
        if (request.getOccupation() != null) map.add("occupation", request.getOccupation());
        if (request.getSalTp() != null) map.add("salTp", request.getSalTp());
        if (request.getMinPay() != null) map.add("minPay", String.valueOf(request.getMinPay()));
        if (request.getMaxPay() != null) map.add("maxPay", String.valueOf(request.getMaxPay()));
        if (request.getEducation() != null) map.add("education", request.getEducation());
        if (request.getCareer() != null) map.add("career", request.getCareer());
        if (request.getMinCareerM() != null) map.add("minCareerM", String.valueOf(request.getMinCareerM()));
        if (request.getMaxCareerM() != null) map.add("maxCareerM", String.valueOf(request.getMaxCareerM()));
        if (request.getPref() != null) map.add("pref", request.getPref());
        if (request.getSubway() != null) map.add("subway", request.getSubway());
        if (request.getEmpTp() != null) map.add("empTp", request.getEmpTp());
        if (request.getTermContractMmcnt() != null) map.add("termContractMmcnt", request.getTermContractMmcnt());
        if (request.getHolidayTp() != null) map.add("holidayTp", request.getHolidayTp());
        if (request.getCoTp() != null) map.add("coTp", request.getCoTp());
        if (request.getBusino() != null) map.add("busino", request.getBusino());
        if (request.getDtlSmlgntYn() != null) map.add("dtlSmlgntYn", request.getDtlSmlgntYn());
        if (request.getWorkStudyJoinYn() != null) map.add("workStudyJoinYn", request.getWorkStudyJoinYn());
        if (request.getSmlgntCoClcd() != null) map.add("smlgntCoClcd", request.getSmlgntCoClcd());
        if (request.getWorkerCnt() != null) map.add("workerCnt", request.getWorkerCnt());
        if (request.getWelfare() != null) map.add("welfare", request.getWelfare());
        if (request.getCertLic() != null) map.add("certLic", request.getCertLic());
        if (request.getRegDate() != null) map.add("regDate", request.getRegDate());
        if (request.getUntilEmpWantedYn() != null) map.add("untilEmpWantedYn", request.getUntilEmpWantedYn());
        if (request.getMinWantedAuthDt() != null) map.add("minWantedAuthDt", request.getMinWantedAuthDt());
        if (request.getMaxWantedAuthDt() != null) map.add("maxWantedAuthDt", request.getMaxWantedAuthDt());
        if (request.getEmpTpGb() != null) map.add("empTpGb", request.getEmpTpGb());
        if (request.getMajor() != null) map.add("major", request.getMajor());
        if (request.getForeignLanguage() != null) map.add("foreignLanguage", request.getForeignLanguage());
        if (request.getComPreferential() != null) map.add("comPreferential", request.getComPreferential());
        if (request.getPfPreferential() != null) map.add("pfPreferential", request.getPfPreferential());
        if (request.getWorkHrCd() != null) map.add("workHrCd", request.getWorkHrCd());
        if (request.getKeyword() != null && !request.getKeyword().isBlank()) {
            map.add("keyword", request.getKeyword());
        }
        if (request.getSortOrderBy() != null) map.add("sortOrderBy", request.getSortOrderBy());

        return map;
    }


    public Mono<WorknetApiResponse> getForeignerJobPostings(String keyword) {
        List<String> keys = (keyword == null || keyword.isBlank())
                ? List.of("외국인", "외국인우대", "E-7", "E7", "E-9", "E9", "D-10", "F-2", "F-4", "F-6")
                : List.of(keyword, keyword + " 외국인", keyword + " 비자");

        return Flux.fromIterable(keys)
                .flatMap(k -> {
                    WorknetApiRequest request = WorknetApiRequest.builder().keyword(k).build();
                    return this.webClient.get().uri(uriBuilder -> uriBuilder
                                    .queryParams(toMultiValueMap(request))
                                    .build())
                            .retrieve()
                            .bodyToMono(String.class)
                            .flatMap(body -> {
                                log.debug("Raw response for keyword '{}': {}", k, body);
                                try {
                                    return Mono.just(xmlMapper.readValue(body, WorknetApiResponse.class));
                                } catch (JsonProcessingException e) {
                                    log.warn("Could not parse Worknet response for keyword '{}'. Body: {}", k, body);
                                    return Mono.empty();
                                }
                            })
                            .doOnNext(response -> {
                                if (response.getError() != null) {
                                    log.warn("Worknet API error for keyword '{}': {}", k, response.getError());
                                }
                            })
                            .doOnError(e -> log.error("API call failed for keyword: {}", k, e))
                            .onErrorResume(e -> Mono.empty()) // Continue flux even if one call fails
                            .map(resp -> Optional.ofNullable(resp.getWanted()).orElseGet(List::of));
                })
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
                        merged.setDisplay(list.size());
                        merged.setStartPage(1);
                    } catch (Exception ignore) {
                        log.error("Failed to set 'wanted' field via reflection", ignore);
                    }
                    return merged;
                });
    }
}
