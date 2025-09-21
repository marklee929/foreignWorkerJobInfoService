package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import lombok.Data;

import java.util.List;

@Data
public class WorknetApiResponse {

    // Fields for success response (<wantedRoot>)
    @JacksonXmlProperty(localName = "total")
    private Integer total;

    @JacksonXmlProperty(localName = "startPage")
    private Integer startPage;

    @JacksonXmlProperty(localName = "display")
    private Integer display;

    @JacksonXmlElementWrapper(useWrapping = false)
    @JacksonXmlProperty(localName = "wanted")
    private List<WorknetJobPost> wanted;

    // Field for error response (<GO24>)
    @JacksonXmlProperty(localName = "error")
    private String error;
}
