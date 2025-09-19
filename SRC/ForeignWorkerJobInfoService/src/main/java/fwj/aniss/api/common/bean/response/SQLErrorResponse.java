package fwj.aniss.api.common.bean.response;

public enum SQLErrorResponse implements BaseAPIResponse {

	DATA_REPROCESSING_ERROR(1000, "데이터 재처리하는 과정에 오류가 발생하였습니다."),
	NO_DATA_HAS_BEEN_CHANGED(1001, "변경된 데이터가 없습니다."),
	ALREADY_PK_DATA(1002, "이미 데이터가 존재합니다. 다시 확인하여 주시기 바랍니다.");

	protected int code;
	protected String message;

	SQLErrorResponse(int code, String message) {
		this.code = code;
		this.message = message;
	}

	@Override
	public int getCode() {
		return this.code;
	}

	@Override
	public String getMessage() {
		return this.message;
	}

}
