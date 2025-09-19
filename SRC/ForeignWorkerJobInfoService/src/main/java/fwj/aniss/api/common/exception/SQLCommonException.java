package fwj.aniss.api.common.exception;

import fwj.aniss.api.common.bean.response.SQLErrorResponse;

public class SQLCommonException extends RuntimeException {

	private static final long serialVersionUID = 8829610180938129782L;

	private int errorCode = 0;

	/**
	 * @param message
	 * @param errorCode
	 */
	public SQLCommonException(SQLErrorResponse sqlErrorResponse) {
		super(sqlErrorResponse.getMessage());
		this.errorCode = sqlErrorResponse.getCode();
	}

	@Override
	public synchronized Throwable fillInStackTrace() {
		return this;
	}

	public static final SQLCommonException DATA_REPROCESSING_ERROR = new SQLCommonException(
			SQLErrorResponse.DATA_REPROCESSING_ERROR);
	public static final SQLCommonException NO_DATA_HAS_BEEN_CHANGED = new SQLCommonException(
			SQLErrorResponse.NO_DATA_HAS_BEEN_CHANGED);
	public static final SQLCommonException ALREADY_PK_DATA = new SQLCommonException(SQLErrorResponse.ALREADY_PK_DATA);
}