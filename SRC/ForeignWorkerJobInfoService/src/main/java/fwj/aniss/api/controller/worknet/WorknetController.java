package fwj.aniss.api.controller.worknet;

import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
import fwj.aniss.api.common.exception.CommonException;
import fwj.aniss.api.common.service.worknet.WorknetApiService;
import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/worknet")
public class WorknetController {

    private final WorknetApiService worknetApiService;

    @GetMapping("/jobs")
    public Mono<WorknetApiResponse> getForeignerJobs(@RequestParam(required = false) String keyword) {
        if (keyword == null || keyword.isBlank()) {
            throw CommonException.INVALID_PARAM;
        }
        return worknetApiService.getForeignerJobPostings(keyword);
    }
}