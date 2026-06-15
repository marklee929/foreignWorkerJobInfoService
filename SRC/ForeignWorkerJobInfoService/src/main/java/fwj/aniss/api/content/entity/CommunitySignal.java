package fwj.aniss.api.content.entity;

import java.math.BigDecimal;
import java.time.OffsetDateTime;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CommunitySignal {
    private Long id;
    private String sourcePlatform;
    private String sourceUrl;
    private String topic;
    private String language;
    private String country;
    private String category;
    private String questionPattern;
    private BigDecimal frequencyScore;
    private BigDecimal urgencyScore;
    private Integer sampleCount;
    private String authorHash;
    private String rawRetentionPolicy;
    private Boolean piiCheckedYn;
    private Boolean usableForContentYn;
    private String termsRiskLevel;
    private OffsetDateTime createdAt;
}
