package fwj.aniss.api.content.telegram;

import org.springframework.stereotype.Service;
import org.telegram.telegrambots.meta.api.objects.CallbackQuery;
import org.telegram.telegrambots.meta.api.objects.MaybeInaccessibleMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.User;

import fwj.aniss.api.content.dto.ContentWorkflowDto.TelegramCallbackRequest;
import fwj.aniss.api.content.model.ContentWorkflowConstants;
import fwj.aniss.api.content.service.ContentApprovalWorkflowService;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TelegramReviewUpdateService {
    private final ContentApprovalWorkflowService workflowService;

    public boolean handleUpdate(Update update) {
        if (update == null || !update.hasCallbackQuery()) {
            return false;
        }
        CallbackQuery callbackQuery = update.getCallbackQuery();
        String data = callbackQuery.getData();
        if (data == null || !data.startsWith(ContentWorkflowConstants.CALLBACK_PREFIX + ":")) {
            return false;
        }

        User from = callbackQuery.getFrom();
        MaybeInaccessibleMessage message = callbackQuery.getMessage();
        Long messageId = message == null ? null : message.getMessageId().longValue();
        workflowService.handleTelegramCallback(new TelegramCallbackRequest(
                null,
                null,
                from == null ? "" : String.valueOf(from.getId()),
                displayName(from),
                "",
                messageId,
                data));
        return true;
    }

    private String displayName(User user) {
        if (user == null) {
            return "";
        }
        if (user.getUserName() != null && !user.getUserName().isBlank()) {
            return user.getUserName();
        }
        String firstName = user.getFirstName() == null ? "" : user.getFirstName();
        String lastName = user.getLastName() == null ? "" : user.getLastName();
        return (firstName + " " + lastName).trim();
    }
}
