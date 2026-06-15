package fwj.aniss.api.content.repository;

import java.util.List;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import fwj.aniss.api.content.entity.ReviewLog;
import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class ReviewLogRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public ReviewLog save(ReviewLog log) {
        String sql = """
                INSERT INTO content.review_log (
                    generated_content_id, review_channel, telegram_message_id,
                    reviewer_id, reviewer_name, action, comment, reviewed_at
                ) VALUES (
                    :generatedContentId, :reviewChannel, :telegramMessageId,
                    :reviewerId, :reviewerName, :action, :comment, COALESCE(:reviewedAt, CURRENT_TIMESTAMP)
                )
                """;
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(sql, params(log), keyHolder, new String[] { "id" });
        Number key = keyHolder.getKey();
        log.setId(key == null ? null : key.longValue());
        return log;
    }

    public List<ReviewLog> listByContentId(Long generatedContentId) {
        String sql = """
                SELECT *
                FROM content.review_log
                WHERE generated_content_id = :generatedContentId
                ORDER BY reviewed_at DESC, id DESC
                """;
        return jdbcTemplate.query(sql, new MapSqlParameterSource("generatedContentId", generatedContentId),
                ContentRowMapper::mapReviewLog);
    }

    public List<ReviewLog> list(Long generatedContentId, int limit) {
        StringBuilder sql = new StringBuilder("SELECT * FROM content.review_log WHERE 1 = 1");
        MapSqlParameterSource params = new MapSqlParameterSource("limit", clampLimit(limit));
        if (generatedContentId != null) {
            sql.append(" AND generated_content_id = :generatedContentId");
            params.addValue("generatedContentId", generatedContentId);
        }
        sql.append(" ORDER BY reviewed_at DESC, id DESC LIMIT :limit");
        return jdbcTemplate.query(sql.toString(), params, ContentRowMapper::mapReviewLog);
    }

    private MapSqlParameterSource params(ReviewLog log) {
        return new MapSqlParameterSource()
                .addValue("generatedContentId", log.getGeneratedContentId())
                .addValue("reviewChannel", defaultString(log.getReviewChannel(), "ADMIN"))
                .addValue("telegramMessageId", log.getTelegramMessageId())
                .addValue("reviewerId", defaultString(log.getReviewerId(), ""))
                .addValue("reviewerName", defaultString(log.getReviewerName(), ""))
                .addValue("action", defaultString(log.getAction(), "SENT"))
                .addValue("comment", defaultString(log.getComment(), ""))
                .addValue("reviewedAt", log.getReviewedAt());
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
