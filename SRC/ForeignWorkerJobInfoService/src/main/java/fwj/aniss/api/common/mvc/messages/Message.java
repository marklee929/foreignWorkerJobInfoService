package fwj.aniss.api.common.mvc.messages;

public class Message {

	private String msg;

	private String code;

	public Message(String code, String msg) {
		this.setCode(code);
		this.setMsg(msg);
	}

	public String getMsg() {
		return msg;
	}

	public void setMsg(String msg) {
		this.msg = msg;
	}

	public String getCode() {
		return code;
	}

	public void setCode(String code) {
		this.code = code;
	}
}