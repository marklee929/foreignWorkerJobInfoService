package fwj.aniss.api.common.utils.telegrambot;

import java.util.Properties;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.api.methods.BotApiMethod;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.generics.BotSession;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;

import jakarta.annotation.PostConstruct; // PostConstruct import 추가
import jakarta.annotation.PreDestroy; // PreDestroy import 추가
import fwj.aniss.api.common.utils.CommonUtils;

@Component
public class Bot extends TelegramLongPollingBot {

    private String botUsername;
    private String botToken;

    private TelegramBotsApi botsApi;

    private BotSession botSession;

    @Value("${spring.profile.value}")
    private String ENV;

    // @Autowired
    // private MemberService memberService;

    // @PostConstruct를 사용하여 빈 초기화 시점에 봇 등록
    @PostConstruct
    public void init() {
        if ("local".equals(ENV)) {
            return;
        }

        Properties prop = CommonUtils.readProperties(Bot.class, "application.properties"); // application-own.properties
                                                                                           // 대신 application.properties
                                                                                           // 사용
        botUsername = prop.getProperty("telegram.webhook.url");
        botToken = prop.getProperty("telegram.api.key");

        if ((StringUtils.isNotEmpty(botToken)) && StringUtils.isNotEmpty(botUsername)) {
            try {
                if (botsApi == null) {
                    botsApi = new TelegramBotsApi(DefaultBotSession.class);
                }
                // 봇이 이미 등록되어 있지 않은 경우에만 등록
                if (botSession == null || !botSession.isRunning()) {
                    botSession = botsApi.registerBot(this);
                }
            } catch (TelegramApiException e) {
                e.printStackTrace();
            }
        }
    }

    // 애플리케이션 종료 시 봇 세션 종료
    @PreDestroy
    public void destroy() {
        if (botSession != null && botSession.isRunning()) {
            botSession.stop();
            System.out.println("Telegram Bot session stopped.");
        }
    }

    @Override
    public String getBotUsername() {
        return botUsername;
    }

    @Override
    public String getBotToken() {
        return botToken;
    }

    public boolean isActive() {
        return botSession != null && botSession.isRunning();
    }

    @Override
    public void onUpdateReceived(Update update) {
        if (update.hasMessage() && update.getMessage().hasText()) {
            String messageText = update.getMessage().getText();
            long chatId = update.getMessage().getChatId();

            System.out.println("입력받은 메세지 : " + chatId + " : " + messageText);
            if (messageText.equals("/start")) {
                sendTextMessage(String.valueOf(chatId), "회원 아이디를 (id:*****) 형태로 입력해주세요. (예===> id:itbong )");
            }

            // if (messageText.toLowerCase().contains("id:")) {
            // String memberId = messageText.trim().substring(3, messageText.length());

            // MemberBean memberParam = new MemberBean();
            // memberParam.setMemberId(memberId);

            // MemberBean member = null;
            // try {
            // member = memberService.selectMemberInfo(memberParam);
            // } catch (Exception e) {
            // // TODO Auto-generated catch block
            // e.printStackTrace();
            // }

            // if (member != null) {
            // MemberBean updateMember = new MemberBean();
            // updateMember.setMemberNo(member.getMemberNo());
            // updateMember.setTelegramChannelId(String.valueOf(chatId));

            // int res = memberService.updateMemberInfo(updateMember);

            // if (res > 0) {
            // sendTextMessage(String.valueOf(chatId), "회원님은 이제부터 텔레그램을 통해 메세지를 전달받으실 수
            // 있습니다.");
            // } else {
            // sendTextMessage(String.valueOf(chatId), "서버장애로 업데이트 되지않았습니다. 잠시후 다시 시도해주세.");
            // }
            // } else {
            // sendTextMessage(String.valueOf(chatId), "입력하신 아이디로 조회되는 회원이 존재하지 않습니다.");
            // }
            // // 이 부분은 중복된 코드이므로 제거하거나 수정해야 합니다.
            // // int res = memberService.updateMemberInfo(member);
            // // if(res > 0) {
            // // }
            // }
        }
    }

    public void sendTextMessage(String chatId, String text) {
        if (botSession == null || !botSession.isRunning()) {
            System.err.println("Telegram Bot session is not active. Message not sent.");
            return;
        }

        SendMessage message = new SendMessage();
        message.setChatId(chatId);
        message.setText(text);

        sendMessage(message);
    }

    public void sendMessage(BotApiMethod<?> message) {
        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }
}