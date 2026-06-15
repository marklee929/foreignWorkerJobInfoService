package fwj.aniss.api.content.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import fwj.aniss.api.content.dto.ContentWorkflowDto.GeneratedContentResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.TelegramCallbackRequest;
import fwj.aniss.api.content.service.ContentApprovalWorkflowService;
import lombok.RequiredArgsConstructor;

@RestController
@RequiredArgsConstructor
public class TelegramReviewCallbackController {
    private final ContentApprovalWorkflowService workflowService;

    @PostMapping("/api/telegram/review-callback")
    public GeneratedContentResponse reviewCallback(@RequestBody TelegramCallbackRequest request) {
        return workflowService.handleTelegramCallback(request);
    }
}
