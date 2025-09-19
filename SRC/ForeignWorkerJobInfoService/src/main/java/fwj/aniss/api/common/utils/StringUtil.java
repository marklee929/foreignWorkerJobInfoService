package fwj.aniss.api.common.utils;

import java.io.PrintWriter;
import java.io.StringWriter;

public class StringUtil  {


	/**
	 * Exception Trace String 으로 변환
	 */
	public static String getExceptionMsg(Exception e) {
		 // StringWriter와 PrintWriter를 사용하여 스택 트레이스를 문자열로 변환
	    StringWriter sw = new StringWriter();
	    PrintWriter pw = new PrintWriter(sw);
	    e.printStackTrace(pw);
	    String stackTrace = sw.toString();
	    //System.out.println("스택 트레이스: " + stackTrace);
	    
	    return stackTrace;
	}

}