package fwj.aniss.api.content.controller;

import java.util.Map;

import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import fwj.aniss.api.content.service.ContentWorkflowException;

@Order(Ordered.HIGHEST_PRECEDENCE)
@RestControllerAdvice(assignableTypes = {
        ContentApprovalWorkflowController.class,
        TelegramReviewCallbackController.class
})
public class ContentWorkflowExceptionAdvice {
    @ExceptionHandler(ContentWorkflowException.class)
    public ResponseEntity<Map<String, Object>> handleContentWorkflowException(ContentWorkflowException exception) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(Map.of(
                        "result", "FAIL",
                        "message", exception.getMessage()));
    }
}
