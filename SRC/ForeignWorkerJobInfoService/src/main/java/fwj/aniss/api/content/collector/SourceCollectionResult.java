package fwj.aniss.api.content.collector;

import java.util.List;

import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemInput;

public record SourceCollectionResult(
        List<SourceItemInput> sourceItems,
        List<CommunitySignalRequest> communitySignals) {

    public SourceCollectionResult {
        sourceItems = sourceItems == null ? List.of() : List.copyOf(sourceItems);
        communitySignals = communitySignals == null ? List.of() : List.copyOf(communitySignals);
    }

    public static SourceCollectionResult empty() {
        return new SourceCollectionResult(List.of(), List.of());
    }

    public static SourceCollectionResult sourceItems(List<SourceItemInput> sourceItems) {
        return new SourceCollectionResult(sourceItems, List.of());
    }

    public static SourceCollectionResult communitySignals(List<CommunitySignalRequest> communitySignals) {
        return new SourceCollectionResult(List.of(), communitySignals);
    }

    public int collectedCount() {
        return sourceItems.size() + communitySignals.size();
    }
}
