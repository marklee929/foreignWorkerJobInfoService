package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import lombok.Data;

@Data
public class WorknetJobPost {

    /**
     * 구인인증번호
     */
    @JacksonXmlProperty(localName = "wantedAuthNo")
    private String wantedAuthNo;

    /**
     * 회사명
     */
    @JacksonXmlProperty(localName = "company")
    private String company;

    /**
     * 사업자등록번호
     */
    @JacksonXmlProperty(localName = "busino")
    private String busino;

    /**
     * 업종
     */
    @JacksonXmlProperty(localName = "indTpNm")
    private String indTpNm;

    /**
     * 채용제목
     */
    @JacksonXmlProperty(localName = "title")
    private String title;

    /**
     * 임금형태
     */
    @JacksonXmlProperty(localName = "salTpNm")
    private String salTpNm;

    /**
     * 급여
     */
    @JacksonXmlProperty(localName = "sal")
    private String sal;

    /**
     * 최소임금액
     */
    @JacksonXmlProperty(localName = "minSal")
    private String minSal;

    /**
     * 최대임금액
     */
    @JacksonXmlProperty(localName = "maxSal")
    private String maxSal;

    /**
     * 근무지역
     */
    @JacksonXmlProperty(localName = "region")
    private String region;

    /**
     * 근무형태
     */
    @JacksonXmlProperty(localName = "holidayTpNm")
    private String holidayTpNm;

    /**
     * 최소학력
     */
    @JacksonXmlProperty(localName = "minEdubg")
    private String minEdubg;

    /**
     * 최대학력
     */
    @JacksonXmlProperty(localName = "maxEdubg")
    private String maxEdubg;

    /**
     * 경력
     */
    @JacksonXmlProperty(localName = "career")
    private String career;

    /**
     * 등록일자
     */
    @JacksonXmlProperty(localName = "regDt")
    private String regDt;

    /**
     * 마감일자
     */
    @JacksonXmlProperty(localName = "closeDt")
    private String closeDt;

    /**
     * 정보제공처 (VALIDATION: 워크넷 인증)
     */
    @JacksonXmlProperty(localName = "infoSvc")
    private String infoSvc;

    /**
     * 워크넷 채용정보 URL
     */
    @JacksonXmlProperty(localName = "wantedInfoUrl")
    private String wantedInfoUrl;

    /**
     * 워크넷 모바일 채용정보 URL
     */
    @JacksonXmlProperty(localName = "wantedMobileInfoUrl")
    private String wantedMobileInfoUrl;

    /**
     * 근무지 우편주소
     */
    @JacksonXmlProperty(localName = "zipCd")
    private String zipCd;

    /**
     * 근무지 도로명주소
     */
    @JacksonXmlProperty(localName = "strtnmCd")
    private String strtnmCd;

    /**
     * 근무지 기본주소
     */
    @JacksonXmlProperty(localName = "basicAddr")
    private String basicAddr;

    /**
     * 근무지 상세주소
     */
    @JacksonXmlProperty(localName = "detailAddr")
    private String detailAddr;

    /**
     * 고용형태코드 (10: 기간의 정함이 없는 근로계약, 11: 기간의 정함이 없는 근로계약(시간(선택)제), 20: 기간의 정함이 있는 근로계약, 21: 기간의 정함이 있는 근로계약(시간(선택)제))
     */
    @JacksonXmlProperty(localName = "empTpCd")
    private String empTpCd;

    /**
     * 직종코드
     */
    @JacksonXmlProperty(localName = "jobsCd")
    private String jobsCd;

    /**
     * 최종수정일
     */
    @JacksonXmlProperty(localName = "smodifyDtm")
    private String smodifyDtm;
}
