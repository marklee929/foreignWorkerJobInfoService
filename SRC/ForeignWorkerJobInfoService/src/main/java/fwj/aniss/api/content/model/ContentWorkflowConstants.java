package fwj.aniss.api.content.model;

public final class ContentWorkflowConstants {
    private ContentWorkflowConstants() {
    }

    public static final String STATUS_COLLECTED = "COLLECTED";
    public static final String STATUS_GENERATED = "GENERATED";
    public static final String STATUS_SENT_TO_TELEGRAM = "SENT_TO_TELEGRAM";
    public static final String STATUS_APPROVED = "APPROVED";
    public static final String STATUS_REJECTED = "REJECTED";
    public static final String STATUS_PUBLISHED = "PUBLISHED";

    public static final String REVIEW_CHANNEL_TELEGRAM = "TELEGRAM";
    public static final String REVIEW_CHANNEL_ADMIN = "ADMIN";
    public static final String REVIEW_CHANNEL_SCHEDULER = "SCHEDULER";

    public static final String ACTION_SENT = "SENT";
    public static final String ACTION_APPROVED = "APPROVED";
    public static final String ACTION_REJECTED = "REJECTED";
    public static final String ACTION_EDIT_REQUESTED = "EDIT_REQUESTED";

    public static final String CALLBACK_PREFIX = "content_review";
}
