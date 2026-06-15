package fwj.aniss.api.content.scheduler;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectResponse;
import fwj.aniss.api.content.service.ContentApprovalWorkflowService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class ContentWorkflowScheduler {
    private final ContentApprovalWorkflowService workflowService;

    @Value("${content.scheduler.enabled:false}")
    private boolean schedulerEnabled;

    @Scheduled(fixedDelayString = "${content.scheduler.source-collection-delay-ms:1800000}")
    public void sourceCollection() {
        if (!schedulerEnabled) {
            return;
        }
        SourceCollectResponse response = workflowService.runSourceCollection(20, false);
        log.info("Content source collection scheduler collected {} item(s), created {}, updated {}, blocked {}.",
                response.collected(), response.created(), response.updated(), response.blocked());
    }

    @Scheduled(fixedDelayString = "${content.scheduler.generation-delay-ms:1800000}")
    public void contentGeneration() {
        if (!schedulerEnabled) {
            return;
        }
        int generated = workflowService.generatePendingContent(20);
        log.info("Content generation scheduler generated {} item(s).", generated);
    }

    @Scheduled(fixedDelayString = "${content.scheduler.telegram-delivery-delay-ms:900000}")
    public void telegramDelivery() {
        if (!schedulerEnabled) {
            return;
        }
        int delivered = workflowService.deliverPendingTelegram(20);
        log.info("Telegram delivery scheduler sent {} dry-run review item(s).", delivered);
    }
}
