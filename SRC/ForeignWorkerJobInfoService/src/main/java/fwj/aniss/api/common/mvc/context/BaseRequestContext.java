package fwj.aniss.api.common.mvc.context;

import fwj.aniss.api.common.mvc.messages.MessageAccessor;

/**
 * Message 처리를 위해 사용되는 임시 저장소
 *
 * @author jeado
 *
 */
public class BaseRequestContext {

	private MessageAccessor messageAccessor;

	/**
	 * 클라이언트에 전달한 메시지를 반화한다.
	 *
	 * @return messageAccessor
	 */
	public MessageAccessor getMessageAccessor() {
		return messageAccessor;
	}

	/**
	 * 클라이언트에 전달한 메시지를 설정한다.
	 *
	 * @param messageAccessor
	 */
	public void setMessageAccessor(MessageAccessor messageAccessor) {
		this.messageAccessor = messageAccessor;
	}
}