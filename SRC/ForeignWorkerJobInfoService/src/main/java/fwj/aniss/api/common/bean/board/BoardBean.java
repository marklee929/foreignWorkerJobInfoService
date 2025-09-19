package fwj.aniss.api.common.bean.board;

import lombok.Data;

@Data
public class BoardBean {

    private long boardNo;
    private long memberNo;
    private String title;
    private String content;
    private String regDate;
}
