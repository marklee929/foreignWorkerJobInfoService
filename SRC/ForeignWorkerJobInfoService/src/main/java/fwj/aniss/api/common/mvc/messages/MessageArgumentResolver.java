package fwj.aniss.api.common.mvc.messages;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.MethodParameter;
import org.springframework.web.bind.support.WebDataBinderFactory;
import org.springframework.web.context.request.NativeWebRequest;
import org.springframework.web.method.support.HandlerMethodArgumentResolver;
import org.springframework.web.method.support.ModelAndViewContainer;

import fwj.aniss.api.common.mvc.context.BaseRequestContextHolder;

/**
 * 컨트롤러에 매개변수로 등록된 메시지처리 접근자({@link Messages}) 를 생성하여 컨트롤러에 전달한다.
 * 
 * @author jeado
 *
 */
public class MessageArgumentResolver implements HandlerMethodArgumentResolver {

	private static final Logger LOGGER = LoggerFactory.getLogger(MessageArgumentResolver.class);

	@Override
	public boolean supportsParameter(MethodParameter parameter) {
		return Messages.class.isAssignableFrom(parameter.getParameterType());
	}

	@Override
	public Object resolveArgument(MethodParameter parameter,
			ModelAndViewContainer mavContainer, NativeWebRequest webRequest,
			WebDataBinderFactory binderFactory) {

		LOGGER.debug("Try to inject MessageImpl to Controller {}", parameter.getClass().getName());

		MessagesJsonImpl messagesJsonImpl = new MessagesJsonImpl();

		BaseRequestContextHolder.get().setMessageAccessor(messagesJsonImpl);

		return messagesJsonImpl;
	}

}