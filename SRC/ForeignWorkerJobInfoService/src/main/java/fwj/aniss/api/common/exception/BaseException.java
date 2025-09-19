package fwj.aniss.api.common.exception;

import lombok.*;

/**
 * 기본 Exception
 *
 * @author : mark
 * @date : 2021. 3. 10.
 * @version :
 *
 */
@Data
@EqualsAndHashCode(callSuper = false)
public class BaseException extends Exception {

	private static final long serialVersionUID = 3566636974104600349L;

	private int errorCode = 0;

	public BaseException(String message, int errorCode) {
		super(message);
		this.errorCode = errorCode;
	}

	public int getErrorCode() {
		return errorCode;
	}

	@Override
	public synchronized Throwable fillInStackTrace() {
		return this;
	}
}