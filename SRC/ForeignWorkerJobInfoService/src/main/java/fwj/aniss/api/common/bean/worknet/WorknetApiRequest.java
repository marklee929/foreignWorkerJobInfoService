package fwj.aniss.api.common.bean.worknet;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class WorknetApiRequest {
    /**
     * 인증키
     */
    private String authKey;

    /**
     * 호출할 페이지 타입 (L: 목록, D: 상세)
     */
    @Builder.Default
    private String callTp = "L";

    /**
     * 반환타입 (XML)
     */
    @Builder.Default
    private String returnType = "XML";

    /**
     * 시작페이지
     */
    @Builder.Default
    private Integer startPage = 1;

    /**
     * 목록 수
     */
    @Builder.Default
    private Integer display = 100;

    /**
     * 근무지역코드 (다중검색 가능)
     */
    private String region;

    /**
     * 직종코드 (다중검색 가능)
     */
    private String occupation;

    /**
     * 임금형태 (D: 일급, H: 시급, M: 월급, Y: 연봉)
     */
    private String salTp;

    /**
     * 최소급여
     */
    private Integer minPay;

    /**
     * 최대급여
     */
    private Integer maxPay;

    /**
     * 학력 코드 (00: 학력무관, 01: 초졸이하, 02: 중졸, 03: 고졸, 04: 대졸(2~3년), 05: 대졸(4년), 06: 석사, 07: 박사)
     */
    private String education;

    /**
     * 경력 코드 (N: 신입, E: 경력, Z: 관계없음)
     */
    private String career;

    /**
     * 경력 최소개월 수
     */
    private Integer minCareerM;

    /**
     * 경력 최대개월 수
     */
    private Integer maxCareerM;

    /**
     * 우대조건 (Y: 장애인 병행채용, D: 장애인만 채용) (다중검색 가능)
     */
    private String pref;

    /**
     * 역세권 코드 (다중검색 가능)
     */
    private String subway;

    /**
     * 고용형태 (4: 파견근로, 10: 기간의 정함이 없는 근로계약, 11: 기간의 정함이 없는 근로계약(시간(선택)제), 20: 기간의 정함이 있는 근로계약, 21: 기간의 정함이 있는 근로계약(시간(선택)제), Y: 대체인력채용) (다중검색 가능)
     */
    private String empTp;

    /**
     * 근무기간 (1: 1~3개월, 3: 3~6개월, 6: 6~12개월, 12: 12개월 이상) (다중검색 가능)
     */
    private String termContractMmcnt;

    /**
     * 근무형태 (1: 주 5일 근무, 2: 주 6일 근무, 3: 토요 격주 휴무, 9: 기타) (다중검색 가능)
     */
    private String holidayTp;

    /**
     * 기업형태 (01: 대기업, 03: 벤처기업, 04: 공공기관, 05: 외국계기업, 09: 청년친화강소기업) (다중검색 가능)
     */
    private String coTp;

    /**
     * 사업자등록번호
     */
    private String busino;

    /**
     * 강소기업 여부 (Y)
     */
    private String dtlSmlgntYn;

    /**
     * 일학습병행기업 여부(Y)
     */
    private String workStudyJoinYn;

    /**
     * 강소기업 분류코드
     */
    private String smlgntCoClcd;

    /**
     * 사원수 (W5: 5인 미만, W9: 5인 ~ 10인, W10: 10인 ~ 30인, W30: 30인 ~ 50인, W50: 50인 ~ 100인, W100: 100인 이상)
     */
    private String workerCnt;

    /**
     * 근무편의 (01: 기숙사, 02: 통근버스, 04: 중식제공(또는 중식비 지원), 11: 차량유지비, 12: 교육비 지원, 13: 자녀학자금 지원, 06: 주택자금 지원, 09: 기타) (다중검색 가능)
     */
    private String welfare;

    /**
     * 자격면허 코드 (다중검색 가능)
     */
    private String certLic;

    /**
     * 등록일 (D-0: 오늘, D-3: 3일, M-1: 한달, W-1: 1주 이내, W-2: 2주 이내)
     */
    private String regDate;

    /**
     * 채용시까지 구인여부 (Y/N)
     */
    private String untilEmpWantedYn;

    /**
     * 최소 구인인증일자
     */
    private String minWantedAuthDt;

    /**
     * 최대 구인인증일자
     */
    private String maxWantedAuthDt;

    /**
     * 채용구분 (1: 상용직, 2: 일용직)
     */
    private String empTpGb;

    /**
     * 전공코드 (다중검색 가능)
     */
    private String major;

    /**
     * 외국어코드 (다중검색 가능)
     */
    private String foreignLanguage;

    /**
     * 기타 우대조건 (컴퓨터 활용) (1: 문서작성, 2:스프레드시트, 4: 프리젠테이션, 6: 회계프로그램, 9: 기타) (다중검색 가능)
     */
    private String comPreferential;

    /**
     * 기타 우대조건 (일반) (05: 차량소지자, 07: 고용촉진장려금대상자, 08: 보훈취업지원대상자, 09: 장기복무 제대군인, 10: 북한이탈주민, 14: 운전가능자, S: 장애인, B: (준)고령자(50세이상)) (다중검색 가능)
     */
    private String pfPreferential;

    /**
     * 근무시간 (1: 오전, 2: 오후, 3: 저녁, 4: 새벽, 5: 오전~오후, 6: 오후~저녁, 7: 저녁~새벽, 8: 새벽~오전, 9: 종일 근무, 99: 시간협의/무관) (다중검색 가능)
     */
    private String workHrCd;

    /**
     * 키워드검색 (UTF-8 인코딩) (다중검색 가능)
     */
    private String keyword;

    /**
     * 등록일 기준 정렬방식 (DESC: 내림차순, ASC: 오름차순)
     */
    private String sortOrderBy;
}
