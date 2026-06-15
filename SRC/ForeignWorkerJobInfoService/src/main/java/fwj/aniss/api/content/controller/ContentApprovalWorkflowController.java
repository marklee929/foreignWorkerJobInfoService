package fwj.aniss.api.content.controller;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import fwj.aniss.api.content.dto.ContentWorkflowDto.ContentDashboardResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.CommunitySignalResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.E2eDryRunResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.GenerateContentRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.GeneratedContentResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.PublishTargetResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ReviewActionRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.ReviewLogResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SendTelegramRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCatalogResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectRequest;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCollectResponse;
import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceItemResponse;
import fwj.aniss.api.content.service.ContentApprovalWorkflowService;
import lombok.RequiredArgsConstructor;

@RestController
@RequiredArgsConstructor
public class ContentApprovalWorkflowController {
    private final ContentApprovalWorkflowService workflowService;

    @PostMapping("/api/admin/sources/collect")
    public SourceCollectResponse collectSources(@RequestBody(required = false) SourceCollectRequest request) {
        return workflowService.collectSources(request);
    }

    @GetMapping("/api/admin/source-items")
    public List<SourceItemResponse> sourceItems(
            @RequestParam(required = false) String domain,
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "50") int limit,
            @RequestParam(defaultValue = "0") int offset) {
        return workflowService.listSources(domain, category, limit, offset);
    }

    @PostMapping("/api/admin/content/generate")
    public List<GeneratedContentResponse> generateContent(@RequestBody(required = false) GenerateContentRequest request) {
        return workflowService.generateContent(request);
    }

    @PostMapping("/api/admin/content/e2e-dry-run")
    public E2eDryRunResponse e2eDryRun() {
        return workflowService.e2eDryRun();
    }

    @PostMapping("/api/admin/content/{id}/send-telegram")
    public GeneratedContentResponse sendTelegram(
            @PathVariable Long id,
            @RequestBody(required = false) SendTelegramRequest request) {
        return workflowService.sendToTelegram(id, request);
    }

    @PostMapping("/api/admin/content/{id}/approve")
    public GeneratedContentResponse approve(
            @PathVariable Long id,
            @RequestBody(required = false) ReviewActionRequest request) {
        return workflowService.approve(id, request, "ADMIN");
    }

    @PostMapping("/api/admin/content/{id}/reject")
    public GeneratedContentResponse reject(
            @PathVariable Long id,
            @RequestBody(required = false) ReviewActionRequest request) {
        return workflowService.reject(id, request, "ADMIN");
    }

    @PostMapping("/api/admin/content/{id}/publish")
    public GeneratedContentResponse publishBlocked(@PathVariable Long id) {
        return workflowService.publishBlocked(id);
    }

    @GetMapping("/api/admin/content/generated")
    public List<GeneratedContentResponse> generatedContent(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "50") int limit,
            @RequestParam(defaultValue = "0") int offset) {
        return workflowService.listGenerated(status, category, limit, offset);
    }

    @GetMapping("/api/admin/content/generated/{id}")
    public GeneratedContentResponse generatedContentDetail(@PathVariable Long id) {
        return workflowService.detail(id);
    }

    @GetMapping("/api/admin/content-review/dashboard")
    public ContentDashboardResponse dashboard() {
        return workflowService.dashboard();
    }

    @GetMapping("/api/admin/source-catalog")
    public List<SourceCatalogResponse> sourceCatalog() {
        return workflowService.sourceCatalog();
    }

    @GetMapping("/api/admin/review-logs")
    public List<ReviewLogResponse> reviewLogs(
            @RequestParam(required = false) Long contentId,
            @RequestParam(defaultValue = "50") int limit) {
        return workflowService.reviewLogs(contentId, limit);
    }

    @GetMapping("/api/admin/content/publish-targets")
    public List<PublishTargetResponse> publishTargets(
            @RequestParam(required = false) Long contentId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "50") int limit) {
        return workflowService.publishTargets(contentId, status, limit);
    }

    @GetMapping("/api/admin/community-signals")
    public List<CommunitySignalResponse> communitySignals(
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "50") int limit) {
        return workflowService.communitySignals(category, limit);
    }

    @PostMapping("/api/admin/community-signals")
    public CommunitySignalResponse createCommunitySignal(@RequestBody CommunitySignalRequest request) {
        return workflowService.saveCommunitySignal(request);
    }
}
