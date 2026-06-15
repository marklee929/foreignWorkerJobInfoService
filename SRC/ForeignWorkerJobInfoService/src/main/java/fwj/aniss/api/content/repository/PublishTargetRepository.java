package fwj.aniss.api.content.repository;

import java.util.List;

import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Repository;

import fwj.aniss.api.content.entity.PublishTarget;
import lombok.RequiredArgsConstructor;

@Repository
@RequiredArgsConstructor
public class PublishTargetRepository {
    private final NamedParameterJdbcTemplate jdbcTemplate;

    public void upsertPending(Long generatedContentId, String targetChannel) {
        String sql = """
                INSERT INTO content.publish_target (generated_content_id, target_channel, publish_status)
                VALUES (:generatedContentId, :targetChannel, 'PENDING')
                ON CONFLICT (generated_content_id, target_channel) DO NOTHING
                """;
        jdbcTemplate.update(sql, new MapSqlParameterSource()
                .addValue("generatedContentId", generatedContentId)
                .addValue("targetChannel", targetChannel));
    }

    public List<PublishTarget> list(Long generatedContentId, String status, int limit) {
        StringBuilder sql = new StringBuilder("SELECT * FROM content.publish_target WHERE 1 = 1");
        MapSqlParameterSource params = new MapSqlParameterSource("limit", clampLimit(limit));
        if (generatedContentId != null) {
            sql.append(" AND generated_content_id = :generatedContentId");
            params.addValue("generatedContentId", generatedContentId);
        }
        if (status != null && !status.isBlank()) {
            sql.append(" AND publish_status = :status");
            params.addValue("status", status);
        }
        sql.append(" ORDER BY created_at DESC, id DESC LIMIT :limit");
        return jdbcTemplate.query(sql.toString(), params, ContentRowMapper::mapPublishTarget);
    }

    private int clampLimit(int limit) {
        if (limit <= 0) {
            return 50;
        }
        return Math.min(limit, 500);
    }
}
