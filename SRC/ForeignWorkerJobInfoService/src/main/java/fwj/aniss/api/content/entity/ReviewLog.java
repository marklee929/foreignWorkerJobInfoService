package fwj.aniss.api.content.entity;

import java.time.OffsetDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewLog {
    private Long id;
    private Long generatedContentId;
    private String reviewChannel;
    private Long telegramMessageId;
    private String reviewerId;
    private String reviewerName;
    private String action;
    private String comment;
    private OffsetDateTime reviewedAt;
    private OffsetDateTime createdAt;
}
