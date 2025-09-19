package fwj.aniss.api.common.mvc.advisor;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.MethodParameter;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.ErrorResponse;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

import jakarta.servlet.http.HttpServletRequest;
import fwj.aniss.api.common.exception.CommonException;
import fwj.aniss.api.common.utils.ResUtils;

@RestControllerAdvice
public class RestControllerMessageAdvice implements ResponseBodyAdvice<Object> {
    private static final Logger logger = LoggerFactory.getLogger(RestControllerMessageAdvice.class);

    @Override
    public boolean supports(MethodParameter returnType, Class<? extends HttpMessageConverter<?>> converterType) {
        return true;
    }

    public Object beforeBodyWrite(Object body, MethodParameter returnType, MediaType selectedContentType,
            Class<? extends HttpMessageConverter<?>> selectedConverterType, ServerHttpRequest request,
            ServerHttpResponse response) {
        /* API를 통해서 받는것들에 대해서 API 결과 그대로 화면으로 전송 */
        return body;
    }

    /**
     * 기본 예외처리 헨들러, 다른 예외처리 헨들러에서 처리되지 않은 예외들을 처리함
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    @ResponseBody
    public ResponseEntity<Map<String, Object>> handleOtherExceptions(HttpServletRequest request, Exception ex) {
        logger.error("Exception: ", ex); // Use logger to print stack trace instead of ex.printStackTrace();

        String message = ex.getMessage() != null ? ex.getMessage() : "Unknown error occurred";
        Map<String, Object> responseBody = ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(),
                "Exception From : " + request.getRequestURI() + " error : " + message);

        return ResponseEntity.status(HttpStatus.OK).body(responseBody);
    }
}