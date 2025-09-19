package fwj.aniss.api.common.bean.response;

/**
 * @author mark
 * @date 2022.3.10
 * @desc
 *
 */
public enum CommonResponse {
	// 정상처리 코드 200 공통

	// 에러처리 시스템 메세지 500++
	SELECT_PUBLIC_NOTICE_LIST_FAIL(500, "공지사항 조회 실패"),
	SENDING_SMS_FAIL(501, "문자 발송 실패"),
	SMS_KEY_NOT_MATCH(502, "SMS 발송키 비일치"),
	NO_RECEIVER_NUMBER(503, "수신자 번호 없음"),
	NO_SMS_MESSAGE(504, "발송할 메시지 없음"),
	SELECT_CATEGORY_LIST_FAIL(505, "카테고리 목록 조회 실패"),
	REQUIRED_FILE_NOT_FOUND(506, "필수 요청 파일이 없어서 등록 실패"),
	SELECT_BANK_LIST_FAIL(507, "은행 목록 조회 실패"),
	NO_MEMBER_FOUND(508, "멤버가 조회되지 않음"),

	NO_SPACE_ALLOWED(597, "필수값에 공백 또는 NULL을 사용할 수 없습니다."),
	INVALID_PARAM(598, "잘못된 파라미터"),
	INTERNAL_ERROR(599, "시스템 장애"),
	INSERT_UPDATE_ERROR(400, "DB 등록수정 오류"),
	USER_ADDRESS_LIMIT(517, "등록 가능한 주소를 초과하였습니다. (최대 3개)"),

	// APP/WEB에 alert message요청시 1000++ 코드
	// ACCOUNT_NOT_APPROVED(1000, "승인되지않은 가입정보입니다. 승인될때까지 기다려주세요."),
	TEST(1000, "test");

	protected int code;
	protected String message;

	CommonResponse(int code, String message) {
		this.code = code;
		this.message = message;
	}

	public int getCode() {
		return this.code;
	}

	public String getMessage() {
		return this.message;
	}
}