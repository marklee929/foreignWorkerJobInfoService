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
public class PublishTarget {
    private Long id;
    private Long generatedContentId;
    private String targetChannel;
    private String publishStatus;
    private String publishedUrl;
    private String externalPostId;
    private OffsetDateTime publishedAt;
    private String errorCategory;
    private String errorMessage;
    private String requestPayload;
    private String responsePayload;
    private OffsetDateTime createdAt;
}
