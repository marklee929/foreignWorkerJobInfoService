package fwj.aniss.api.common.mvc.messages;

import fwj.aniss.api.common.bean.response.BaseAPIResponse;
import fwj.aniss.api.common.constants.Constants;

public class MessagesJsonImpl implements Messages, MessageAccessor {

	private Message messages;

	@Override
	public void addMessage(String code, String msg) {
		messages = new Message(code, msg);
	}

	@Override
	public void addMessage(BaseAPIResponse response) {
		if (response.getCode() == 200 || response.getCode() == 201)
			messages = new Message(Constants.RESULT_VAL_OK, response.getMessage());
		else if (response.getCode() >= 1000 && response.getCode() <= 1500)
			messages = new Message(String.valueOf(response.getCode()), response.getMessage());
		else if (response.getCode() == 999)
			messages = new Message("overpending", response.getMessage());
		else
			messages = new Message(Constants.RESULT_VAL_FAIL, response.getMessage());
	}

	@Override
	public Message getMessages() {
		if (messages == null) {
			messages = new Message(Constants.RESULT_VAL_OK, Constants.RESULT_VAL_SUCCESS_MSG);
		}
		return messages;
	}

}