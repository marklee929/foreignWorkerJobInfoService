package fwj.aniss.api.common.utils;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.time.LocalTime;
import java.util.HashMap;
import java.util.Map;

/**
 * 로그유틸 
 * 
 * @author itbong
 * @since 2023.10.04
 */
public class LogUtil {

	private static Map<Long, String> mLogMap = new HashMap<>();
	private static long mLastLogNo = 0;
	
	
	public static synchronized void printLog(long logNo, String logStr, org.slf4j.Logger logger) {
		String nowStr = LocalTime.now().toString();
		
mLastLogNo = logNo;
		//로그 저장
		String bLog = mLogMap.get(logNo);
		if(bLog == null) bLog = "";
		
		String cLog = nowStr + "   " + logStr;
		mLogMap.put(logNo, bLog + cLog + "\n");
		
		//출력
		System.out.println( cLog );
		if(logger != null) {
			logger.info( cLog );
		}
	}
	
	public static void printLog(long longNo, Throwable e) {
		printLog(longNo, getPrintStackTrace(e), null);
	}
	
	public static void printLog(String logStr, org.slf4j.Logger logger) {
		printLog(mLastLogNo, logStr, logger);
	}
	
	public static long getLastLogNo() {
		return mLastLogNo;
	}
	

	public static String getLog(long logNo, boolean isDelLog) {
		String rtnLog = mLogMap.get(logNo);
		if(isDelLog) {
			mLogMap.put(logNo, null);
		}
		return rtnLog;
	}
	
	public static void delLog(long logNo) {
		mLogMap.remove(new Long(logNo));
	}

	public static String getPrintStackTrace(Throwable e) {
        StringWriter errors = new StringWriter();
        e.printStackTrace(new PrintWriter(errors));
         
        return errors.toString();
    }
	
}