package fwj.aniss.api.common.utils;

import java.util.LinkedHashMap;
import java.util.Map;

import fwj.aniss.api.common.constants.Constants;

/**
 * 다국어 메시지 처리 Util
 * 
 * @author Aniss
 * @since 2022.4.14
 */
public class ResUtils {

	public static Map<String, Object> getMakeDefaultSuccessResultMsg(String requestUrl, Object data) {
		Map<String, Object> rtnMap = new LinkedHashMap<String, Object>();

		rtnMap.put(Constants.RESULT_KEY, Constants.RESULT_VAL_OK);
		rtnMap.put(Constants.RESULT_KEY_MSG, Constants.RESULT_VAL_SUCCESS_MSG);
		rtnMap.put(Constants.RESULT_KEY_DATA, data);

		return rtnMap;
	}

	public static Map<String, Object> getMakeDefaultFailResultMsg(String requestUrl, String error) {
		Map<String, Object> rtnMap = new LinkedHashMap<String, Object>();

		rtnMap.put(Constants.RESULT_KEY, Constants.RESULT_VAL_FAIL);
		rtnMap.put(Constants.RESULT_KEY_MSG, Constants.RESULT_VAL_FAIL_MSG + error != null ? error : "");
		rtnMap.put(Constants.RESULT_KEY_DATA, null);

		return rtnMap;
	}

	public static Map<String, Object> getMakeFailResultMsg(String requestUrl, int code, String error) {
		Map<String, Object> rtnMap = new LinkedHashMap<String, Object>();

		rtnMap.put(Constants.RESULT_KEY, code);
		rtnMap.put(Constants.RESULT_KEY_MSG, Constants.RESULT_VAL_FAIL_MSG + error != null ? error : "");
		rtnMap.put(Constants.RESULT_KEY_DATA, null);

		return rtnMap;
	}

	public static Map<String, Object> getMakeResultMsg(String requestUrl, String result, String resultMsg,
			Object data) {
		Map<String, Object> rtnMap = new LinkedHashMap<String, Object>();

		rtnMap.put(Constants.RESULT_KEY, result);
		rtnMap.put(Constants.RESULT_KEY_MSG, resultMsg);
		rtnMap.put(Constants.RESULT_KEY_DATA, data);

		return rtnMap;
	}

	public static Map<String, Object> getMakeResultMsgUpt(Map<String, Object> rtnMap, String result, String resultMsg,
			Object data) {
		rtnMap.put(Constants.RESULT_KEY, result);
		rtnMap.put(Constants.RESULT_KEY_MSG, resultMsg);
		rtnMap.put(Constants.RESULT_KEY_DATA, data);

		return rtnMap;
	}
}