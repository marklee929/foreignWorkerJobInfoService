package fwj.aniss.api.common.bean.worknet;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;
import lombok.Data;

import java.util.List;

@Data
@JacksonXmlRootElement(localName = "wantedRoot")
public class WorknetApiResponse {

    @JacksonXmlProperty(localName = "message")
    private String message;

    @JacksonXmlProperty(localName = "messageCd")
    private String messageCd;

    @JacksonXmlElementWrapper(useWrapping = false)
    @JacksonXmlProperty(localName = "wanted")
    private List<WorknetJobPost> wanted;

    @JacksonXmlProperty(localName = "total")
    private Integer total;

    @JsonIgnore
    public List<WorknetJobPost> getItems() {
        return wanted;
    }
}