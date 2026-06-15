package fwj.aniss.api.content.telegram;

import java.util.List;

import org.springframework.stereotype.Component;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton;

import fwj.aniss.api.content.entity.GeneratedContent;
import fwj.aniss.api.content.model.ContentWorkflowConstants;

@Component
public class TelegramReviewMessageBuilder {
    public String buildMessage(GeneratedContent content) {
        return """
                [WorkConnect Review]

                Content ID: %d
                Type: %s
                Category: %s > %s
                Status: %s
                Risk Score: %s
                Translation: %s%s

                Title:
                %s

                Draft:
                %s

                Summary:
                %s

                Why it matters:
                %s

                Check next:
                %s

                Original:
                %s
                """.formatted(
                content.getId(),
                value(content.getContentType()),
                value(content.getCategory()),
                value(content.getSubcategory()),
                value(content.getStatus()),
                content.getRiskScore() == null ? "0" : content.getRiskScore().toPlainString(),
                Boolean.TRUE.equals(content.getTranslationYn()) ? "YES" : "NO",
                content.getTranslatedFrom() == null || content.getTranslatedFrom().isBlank()
                        ? ""
                        : " from " + content.getTranslatedFrom(),
                value(content.getTitle()),
                truncate(value(content.getWrittenContent()), 1800),
                truncate(value(content.getShortSummary()), 500),
                value(content.getWhyItMatters()),
                truncate(value(content.getCheckNext()), 700),
                value(content.getOriginalLink()));
    }

    public InlineKeyboardMarkup buildKeyboard(Long contentId) {
        InlineKeyboardButton approve = new InlineKeyboardButton("Approve");
        approve.setCallbackData(callbackData("APPROVE", contentId));

        InlineKeyboardButton reject = new InlineKeyboardButton("Reject");
        reject.setCallbackData(callbackData("REJECT", contentId));

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        markup.setKeyboard(List.of(List.of(approve, reject)));
        return markup;
    }

    public String callbackData(String action, Long contentId) {
        return "%s:%s:%d".formatted(ContentWorkflowConstants.CALLBACK_PREFIX, action, contentId);
    }

    private String value(String text) {
        return text == null || text.isBlank() ? "-" : text;
    }

    private String truncate(String text, int maxLength) {
        if (text == null || text.length() <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + "...";
    }
}
