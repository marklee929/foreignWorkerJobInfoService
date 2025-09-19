package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import lombok.Data;

@Data
public class WorknetJobPost {

    @JacksonXmlProperty(localName = "wantedAuthNo")
    private String wantedAuthNo; // 구인인증번호

    @JacksonXmlProperty(localName = "company")
    private String company; // 회사명

    @JacksonXmlProperty(localName = "title")
    private String title; // 채용제목

    @JacksonXmlProperty(localName = "salTpNm")
    private String salTpNm; // 임금형태

    @JacksonXmlProperty(localName = "sal")
    private String sal; // 급여액

    @JacksonXmlProperty(localName = "region")
    private String region; // 근무지역

    @JacksonXmlProperty(localName = "minEdubg")
    private String minEdubg; // 최소학력

    @JacksonXmlProperty(localName = "career")
    private String career; // 경력

    @JacksonXmlProperty(localName = "regDt")
    private String regDt; // 등록일

    @JacksonXmlProperty(localName = "closeDt")
    private String closeDt; // 마감일

    @JacksonXmlProperty(localName = "wantedInfoUrl")
    private String wantedInfoUrl; // 채용정보 URL
}