package fwj.aniss.api.controller.worknet;

import fwj.aniss.api.common.bean.worknet.WorknetApiRequest;
import fwj.aniss.api.common.bean.worknet.WorknetApiResponse;
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

    @GetMapping("/foreigner-jobs")
    public Mono<WorknetApiResponse> getForeignerJobs(@RequestParam(required = false) String keyword) {
        return worknetApiService.getForeignerJobPostings(keyword);
    }

    @GetMapping("/jobs")
    public Mono<WorknetApiResponse> getJobs(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String region,
            @RequestParam(required = false) String occupation,
            @RequestParam(required = false) String salTp,
            @RequestParam(required = false) Integer minPay,
            @RequestParam(required = false) Integer maxPay,
            @RequestParam(required = false) String education,
            @RequestParam(required = false) String career,
            @RequestParam(required = false) Integer minCareerM,
            @RequestParam(required = false) Integer maxCareerM,
            @RequestParam(required = false) String pref,
            @RequestParam(required = false) String subway,
            @RequestParam(required = false) String empTp,
            @RequestParam(required = false) String termContractMmcnt,
            @RequestParam(required = false) String holidayTp,
            @RequestParam(required = false) String coTp,
            @RequestParam(required = false) String busino,
            @RequestParam(required = false) String dtlSmlgntYn,
            @RequestParam(required = false) String workStudyJoinYn,
            @RequestParam(required = false) String smlgntCoClcd,
            @RequestParam(required = false) String workerCnt,
            @RequestParam(required = false) String welfare,
            @RequestParam(required = false) String certLic,
            @RequestParam(required = false) String regDate,
            @RequestParam(required = false) String untilEmpWantedYn,
            @RequestParam(required = false) String minWantedAuthDt,
            @RequestParam(required = false) String maxWantedAuthDt,
            @RequestParam(required = false) String empTpGb,
            @RequestParam(required = false) String major,
            @RequestParam(required = false) String foreignLanguage,
            @RequestParam(required = false) String comPreferential,
            @RequestParam(required = false) String pfPreferential,
            @RequestParam(required = false) String workHrCd,
            @RequestParam(required = false) String sortOrderBy,
            @RequestParam(defaultValue = "1") Integer startPage,
            @RequestParam(defaultValue = "100") Integer display) {

        WorknetApiRequest request = WorknetApiRequest.builder()
                .keyword(keyword)
                .region(region)
                .occupation(occupation)
                .salTp(salTp)
                .minPay(minPay)
                .maxPay(maxPay)
                .education(education)
                .career(career)
                .minCareerM(minCareerM)
                .maxCareerM(maxCareerM)
                .pref(pref)
                .subway(subway)
                .empTp(empTp)
                .termContractMmcnt(termContractMmcnt)
                .holidayTp(holidayTp)
                .coTp(coTp)
                .busino(busino)
                .dtlSmlgntYn(dtlSmlgntYn)
                .workStudyJoinYn(workStudyJoinYn)
                .smlgntCoClcd(smlgntCoClcd)
                .workerCnt(workerCnt)
                .welfare(welfare)
                .certLic(certLic)
                .regDate(regDate)
                .untilEmpWantedYn(untilEmpWantedYn)
                .minWantedAuthDt(minWantedAuthDt)
                .maxWantedAuthDt(maxWantedAuthDt)
                .empTpGb(empTpGb)
                .major(major)
                .foreignLanguage(foreignLanguage)
                .comPreferential(comPreferential)
                .pfPreferential(pfPreferential)
                .workHrCd(workHrCd)
                .sortOrderBy(sortOrderBy)
                .startPage(startPage)
                .display(display)
                .build();

        return worknetApiService.getJobPostings(request);
    }
}
