package fwj.aniss.api.content.service;

import java.util.List;

import org.springframework.stereotype.Service;

import fwj.aniss.api.content.dto.ContentWorkflowDto.SourceCatalogResponse;

@Service
public class SourceCatalogService {
    public List<SourceCatalogResponse> list() {
        return List.of(
                new SourceCatalogResponse("Employment", "EMPLOYMENT", "work24", "Work24", "employment", "SOURCE_BACKED_CONTENT", "API"),
                new SourceCatalogResponse("Employment", "EMPLOYMENT", "worknet", "WorkNet", "employment", "SOURCE_BACKED_CONTENT", "API"),
                new SourceCatalogResponse("Visa", "VISA_IMMIGRATION", "hikorea", "HiKorea", "visa", "OFFICIAL_REVIEW_REQUIRED", "CRAWLER_OR_API"),
                new SourceCatalogResponse("Visa", "VISA_IMMIGRATION", "moj", "Ministry of Justice", "visa", "OFFICIAL_REVIEW_REQUIRED", "CRAWLER_OR_API"),
                new SourceCatalogResponse("Living Information", "LIVING_INFO", "housing", "Housing", "housing", "SOURCE_BACKED_CONTENT", "MANUAL_OR_CRAWLER"),
                new SourceCatalogResponse("Living Information", "LIVING_INFO", "finance", "Finance", "finance", "SOURCE_BACKED_CONTENT", "MANUAL_OR_CRAWLER"),
                new SourceCatalogResponse("Living Information", "LIVING_INFO", "telecom", "Telecom", "telecom", "SOURCE_BACKED_CONTENT", "MANUAL_OR_CRAWLER"),
                new SourceCatalogResponse("Living Information", "LIVING_INFO", "healthcare", "Healthcare", "healthcare", "SOURCE_BACKED_CONTENT", "MANUAL_OR_CRAWLER"),
                new SourceCatalogResponse("Living Information", "LIVING_INFO", "education", "Education", "education", "SOURCE_BACKED_CONTENT", "MANUAL_OR_CRAWLER"),
                new SourceCatalogResponse("Community Signals", "COMMUNITY", "reddit", "Reddit", "community_signal", "TOPIC_SIGNAL_ONLY", "API_WHERE_ALLOWED"),
                new SourceCatalogResponse("Community Signals", "COMMUNITY", "public_community_trend", "Public Community Trend", "community_signal", "TOPIC_SIGNAL_ONLY", "DISCOVERY_ONLY"));
    }
}
