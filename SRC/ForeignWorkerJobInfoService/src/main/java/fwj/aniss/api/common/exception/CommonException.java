package fwj.aniss.api.common.exception;

import fwj.aniss.api.common.bean.response.CommonResponse;

public class CommonException extends BaseException {

    /**
     * serialVersionUID
     */
    private static final long serialVersionUID = 1L;

    /**
     * @param message
     * @param errorCode
     */
    public CommonException(CommonResponse commonStatus) {
        super(commonStatus.getMessage(), commonStatus.getCode());
    }

    public static final CommonException INVALID_PARAM = new CommonException(CommonResponse.INVALID_PARAM);
    public static final CommonException NO_SPACE_ALLOWED = new CommonException(CommonResponse.NO_SPACE_ALLOWED);
    public static final CommonException INTERNAL_ERROR = new CommonException(CommonResponse.INTERNAL_ERROR);
    public static final CommonException SELECT_PUBLIC_NOTICE_LIST_FAIL = new CommonException(
            CommonResponse.SELECT_PUBLIC_NOTICE_LIST_FAIL);
    public static final CommonException SENDING_SMS_FAIL = new CommonException(CommonResponse.SENDING_SMS_FAIL);
    public static final CommonException SMS_KEY_NOT_MATCH = new CommonException(CommonResponse.SMS_KEY_NOT_MATCH);
    public static final CommonException NO_RECEIVER_NUMBER = new CommonException(CommonResponse.NO_RECEIVER_NUMBER);
    public static final CommonException NO_SMS_MESSAGE = new CommonException(CommonResponse.NO_SMS_MESSAGE);
    public static final CommonException SELECT_CATEGORY_LIST_FAIL = new CommonException(
            CommonResponse.SELECT_CATEGORY_LIST_FAIL);
    public static final CommonException REQUIRED_FILE_NOT_FOUND = new CommonException(
            CommonResponse.REQUIRED_FILE_NOT_FOUND);
    public static final CommonException SELECT_BANK_LIST_FAIL = new CommonException(
            CommonResponse.SELECT_BANK_LIST_FAIL);
    public static final CommonException USER_ADDRESS_LIMIT = new CommonException(CommonResponse.USER_ADDRESS_LIMIT);
    public static final CommonException NO_MEMBER_FOUND = new CommonException(CommonResponse.NO_MEMBER_FOUND);

}
