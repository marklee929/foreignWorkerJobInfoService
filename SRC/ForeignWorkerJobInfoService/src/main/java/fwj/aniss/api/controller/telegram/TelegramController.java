package fwj.aniss.api.controller.telegram;

import java.util.concurrent.ConcurrentHashMap;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import fwj.aniss.api.common.utils.telegrambot.Bot;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/telegram")
public class TelegramController {

    private final Bot telegramBot;

    @Value("${telegram.users}")
    private String telegramUsersJson;

    private final ConcurrentHashMap<String, String> telegramIdMap = new ConcurrentHashMap<>();

    @PostConstruct
    public void init() {
        ObjectMapper mapper = new ObjectMapper();
        try {
            JsonNode rootNode = mapper.readTree(telegramUsersJson);
            if (rootNode.isArray()) {
                for (JsonNode node : rootNode) {
                    String name = node.get("memberId").asText();
                    String id = node.get("telegramId").asText();
                    telegramIdMap.put(name, id);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @PostMapping("/sendMessage")
    public ResponseEntity<String> sendMessage(String name, String message) {
        System.out.println("name:" + name + ", message:" + message);
        String chatId = telegramIdMap.get(name);
        if (chatId == null) {
            return ResponseEntity.badRequest().body("Chat ID not found for name: " + name);
        }

        try {
            telegramBot.sendTextMessage(chatId, message);
            return ResponseEntity.ok("Message sent successfully to chat ID: " + chatId);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body("Failed to send message: " + e.getMessage());
        }
    }

    @PostMapping("/sendMessageToAll")
    public ResponseEntity<String> sendMessageToAll(String message) {
        if (telegramIdMap.isEmpty()) {
            return ResponseEntity.badRequest().body("No Telegram users configured in application.properties.");
        }

        StringBuilder successMessages = new StringBuilder();
        StringBuilder errorMessages = new StringBuilder();

        for (String name : telegramIdMap.keySet()) {
            String chatId = telegramIdMap.get(name);
            try {
                telegramBot.sendTextMessage(chatId, message);
                successMessages.append("Message sent to ").append(name).append(" (").append(chatId).append(").\n");
            } catch (Exception e) {
                errorMessages.append("Failed to send message to ").append(name).append(" (").append(chatId)
                        .append("): ").append(e.getMessage()).append(".\n");
            }
        }

        if (errorMessages.length() > 0) {
            return ResponseEntity.internalServerError()
                    .body("Messages sent with some errors:\n" + successMessages.toString() + errorMessages.toString());
        } else {
            return ResponseEntity
                    .ok("Messages sent successfully to all configured Telegram users:\n" + successMessages.toString());
        }
    }
}