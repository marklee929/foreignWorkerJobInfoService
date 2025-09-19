package fwj.aniss.api.common.bean.response;

/**
 * @author mark
 * @date 2022.3.10
 * @desc
 *
 */
public enum AccountResponse implements BaseAPIResponse {
	// 정상처리 코드 200 공통
	DUPLICATE_CHECK_SUCCESS(200, "중복확인 성공"),
	/**
	 * LOGIN_SUCCESS(200, "로그인 성공"),
	 * LOGOUT_SUCCESS(200, "로그아웃 성공"),
	 * ACCOUNT_MOTIFY_SUCCESS(200, "정보 수정완료"),
	 * PASSWORD_CHANGE_SUCCESS(200, "비밀번호 변경완료"),
	 * MODIFY_CERTIFICATION_SUCCESS(200, "본인 인증 처리 성공"),
	 * UNTACT_USER_REGISTER_SUCCESS(200, "비대면 유저 약관동의 정보 등록 생성 성공"),
	 * CHECK_UNTACT_USER_AGREEMENT(200, "비대면 유저 약관동의여부 조회"),
	 * CHECK_UNTACT_USER_CERTIFY(200, "본인인증 완료여부 확인 조회"),
	 * CONFIRM_USER_CERTIFY(200, "본인인증 완료 처리"),
	 * UNTACT_USER_PROFILE(200, "회원 프로필 조회"),
	 * UNTACT_USER_ADDRESS_LIST(200, "회원 주소 목록 조회"),
	 * INSERT_UNTACT_USER_ADDRESS(200, "회원 주소 등록 성공"),
	 * DELETE_UNTACT_USER_ADDRESS(200, "회원 등록 주소 삭제 성공"),
	 */

	// 에러처리 시스템 메세지 500++
	LOGIN_FAIL(500, "로그인 실패"),
	LOGOUT_FAIL(501, "로그아웃 실패"),
	FALSE_LOGIN(502, "잘못된 로그인 요청"),
	ACCOUNT_MOTIFY_FAIL(503, "정보 수정실패"),
	PASSWORD_CHANGE_FAIL(504, "비밀번호 변경실패"),
	DUPLICATE_CHECK_FAIL(505, "중복확인 실패"),
	MODIFY_CERTIFICATION_FAIL(507, "본인 인증 처리 실패"),
	USER_SEARCH_FAIL(507, "회원 조회 실패"),
	INSERT_USER_FAIL(508, "회원 가입 실패"),
	ACCOUNT_NOT_FOUND(509, "온닥터 가입정보 없음"),

	// APP/WEB에 alert message요청시 1000++ 코드
	ACCOUNT_NOT_APPROVED(1000, "승인되지않은 가입정보입니다. 승인될때까지 기다려주세요."),
	WRONG_PASSWORD(1001, "입력하신 암호를 다시 확인해주세요."),
	UNKNOWN_ACCOUNT(1002, "입력하신 정보로 조회되는 정보가 없습니다. 다시 확인해주세요.");

	protected int code;
	protected String message;

	AccountResponse(int code, String message) {
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
