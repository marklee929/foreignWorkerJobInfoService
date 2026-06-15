package fwj.aniss.api.content.collector;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

public interface SourceCollector {
    String sourceDomain();

    String sourcePlatform();

    String sourceName();

    String category();

    SourceCollectionResult collect(SourceCollectRequest request);

    default boolean supports(SourceCollectRequest request) {
        if (request == null) {
            return true;
        }
        String platform = normalize(request.sourcePlatform());
        if (platform != null) {
            return platform.equals(normalize(sourcePlatform()));
        }
        String domain = normalize(request.domain());
        if (domain != null && !domain.equals(normalize(sourceDomain()))) {
            return false;
        }
        String category = normalize(request.category());
        return category == null || category.equals(normalize(category()));
    }

    private static String normalize(String value) {
        return value == null || value.isBlank() ? null : value.trim().toLowerCase();
    }
}
