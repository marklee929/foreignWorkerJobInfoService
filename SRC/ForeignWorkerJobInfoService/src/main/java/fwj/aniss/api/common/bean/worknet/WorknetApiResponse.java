package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
public class WorknetApiResponse {

    @JsonProperty("wanted")
    private List<WorknetJobPost> wanted;

    @JsonProperty("content")
    private List<WorknetJobPost> content;

    @JsonProperty("total")
    private Integer total;

    @JsonIgnore
    public List<WorknetJobPost> getItems() {
        if (wanted != null && !wanted.isEmpty()) {
            return wanted;
        }
        return content;
    }
}