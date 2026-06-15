package fwj.aniss.api.content.repository;

import java.util.List;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import fwj.aniss.api.content.entity.CommunitySignal;
import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class CommunitySignalRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public CommunitySignal save(CommunitySignal signal) {
        String sql = """
                INSERT INTO content.community_signal (
                    source_platform, source_url, topic, language, country, category,
                    question_pattern, frequency_score, urgency_score, sample_count,
                    author_hash, raw_retention_policy, pii_checked_yn,
                    usable_for_content_yn, terms_risk_level
                ) VALUES (
                    :sourcePlatform, :sourceUrl, :topic, :language, :country, :category,
                    :questionPattern, :frequencyScore, :urgencyScore, :sampleCount,
                    :authorHash, :rawRetentionPolicy, :piiCheckedYn,
                    :usableForContentYn, :termsRiskLevel
                )
                """;
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(sql, params(signal), keyHolder, new String[] { "id" });
        Number key = keyHolder.getKey();
        signal.setId(key == null ? null : key.longValue());
        return signal;
    }

    public List<CommunitySignal> list(String category, int limit) {
        StringBuilder sql = new StringBuilder("SELECT * FROM content.community_signal WHERE 1 = 1");
        MapSqlParameterSource params = new MapSqlParameterSource("limit", clampLimit(limit));
        if (category != null && !category.isBlank()) {
            sql.append(" AND category = :category");
            params.addValue("category", category);
        }
        sql.append(" ORDER BY frequency_score DESC, urgency_score DESC, created_at DESC LIMIT :limit");
        return jdbcTemplate.query(sql.toString(), params, ContentRowMapper::mapCommunitySignal);
    }

    private MapSqlParameterSource params(CommunitySignal signal) {
        return new MapSqlParameterSource()
                .addValue("sourcePlatform", defaultString(signal.getSourcePlatform(), ""))
                .addValue("sourceUrl", defaultString(signal.getSourceUrl(), ""))
                .addValue("topic", defaultString(signal.getTopic(), "Untitled topic"))
                .addValue("language", defaultString(signal.getLanguage(), "en"))
                .addValue("country", defaultString(signal.getCountry(), "KR"))
                .addValue("category", defaultString(signal.getCategory(), ""))
                .addValue("questionPattern", defaultString(signal.getQuestionPattern(), ""))
                .addValue("frequencyScore", signal.getFrequencyScore())
                .addValue("urgencyScore", signal.getUrgencyScore())
                .addValue("sampleCount", signal.getSampleCount() == null ? 0 : signal.getSampleCount())
                .addValue("authorHash", defaultString(signal.getAuthorHash(), ""))
                .addValue("rawRetentionPolicy", defaultString(signal.getRawRetentionPolicy(), "ANONYMIZED_SUMMARY_ONLY"))
                .addValue("piiCheckedYn", Boolean.TRUE.equals(signal.getPiiCheckedYn()))
                .addValue("usableForContentYn", Boolean.TRUE.equals(signal.getUsableForContentYn()))
                .addValue("termsRiskLevel", defaultString(signal.getTermsRiskLevel(), "UNKNOWN"));
    }

    private int clampLimit(int limit) {
        if (limit <= 0) {
            return 50;
        }
        return Math.min(limit, 500);
    }

    private String defaultString(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }
}
