
package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class WorknetJobPost {

    @JsonProperty("wantedAuthNo")
    private String wantedAuthNo; // 구인인증번호

    @JsonProperty("company")
    private String company; // 회사명

    @JsonProperty("title")
    private String title; // 채용제목

    @JsonProperty("salTpNm")
    private String salTpNm; // 임금형태

    @JsonProperty("sal")
    private String sal; // 급여액

    @JsonProperty("region")
    private String region; // 근무지역

    @JsonProperty("minEdubg")
    private String minEdubg; // 최소학력

    @JsonProperty("career")
    private String career; // 경력

    @JsonProperty("regDt")
    private String regDt; // 등록일

    @JsonProperty("closeDt")
    private String closeDt; // 마감일

    @JsonProperty("wantedInfoUrl")
    private String wantedInfoUrl; // 채용정보 URL
}
