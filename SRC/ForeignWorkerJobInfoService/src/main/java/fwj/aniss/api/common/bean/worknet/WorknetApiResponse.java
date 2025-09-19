
package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class WorknetApiResponse {

    @JsonProperty("content")
    private List<WorknetJobPost> content;

    @JsonProperty("total")
    private int total;
}
