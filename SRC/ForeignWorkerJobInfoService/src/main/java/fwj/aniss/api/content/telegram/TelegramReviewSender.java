package fwj.aniss.api.content.telegram;

import org.springframework.stereotype.Service;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;

import fwj.aniss.api.common.utils.telegrambot.Bot;
import fwj.aniss.api.content.service.ContentWorkflowException;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TelegramReviewSender {
    private final Bot telegramBot;

    public Long sendReviewCard(String chatId, String message, InlineKeyboardMarkup keyboard) {
        if (chatId == null || chatId.isBlank()) {
            throw new ContentWorkflowException("Telegram review chatId is required.");
        }
        if (!telegramBot.isActive()) {
            throw new ContentWorkflowException("Telegram bot is not active. Use dryRun=true or activate the bot.");
        }
        Integer messageId = telegramBot.sendReviewMessage(chatId, message, keyboard);
        return messageId == null ? null : messageId.longValue();
    }
}
