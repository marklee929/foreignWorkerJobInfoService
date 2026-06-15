package fwj.aniss.api.content.collector;

import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.stereotype.Component;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;

@Component
public class SourceCollectorRegistry {
    private final List<SourceCollector> collectors;
    private final Map<String, SourceCollector> byPlatform;

    public SourceCollectorRegistry(List<SourceCollector> collectors) {
        this.collectors = collectors.stream()
                .sorted(Comparator.comparing(SourceCollector::sourcePlatform))
                .toList();
        this.byPlatform = this.collectors.stream()
                .collect(Collectors.toUnmodifiableMap(
                        collector -> normalize(collector.sourcePlatform()),
                        Function.identity(),
                        (left, right) -> left));
    }

    public List<SourceCollector> all() {
        return collectors;
    }

    public Optional<SourceCollector> findByPlatform(String sourcePlatform) {
        if (sourcePlatform == null || sourcePlatform.isBlank()) {
            return Optional.empty();
        }
        return Optional.ofNullable(byPlatform.get(normalize(sourcePlatform)));
    }

    public List<SourceCollector> matching(SourceCollectRequest request) {
        if (request != null && request.sourcePlatform() != null && !request.sourcePlatform().isBlank()) {
            return findByPlatform(request.sourcePlatform()).stream().toList();
        }
        return collectors.stream()
                .filter(collector -> collector.supports(request))
                .toList();
    }

    private String normalize(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
    }
}
