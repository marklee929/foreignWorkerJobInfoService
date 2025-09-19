package fwj.aniss.api.common.utils;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.Field;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Properties;
import java.util.Random;
import java.util.Set;
import java.util.StringTokenizer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.multipart.MultipartFile;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.servlet.http.HttpServletRequest;
import fwj.aniss.api.common.constants.Constants;

/**
 * 공통사용 Util
 * 
 * @author PCH
 */

public class CommonUtils {
	private static final Log log = LogFactory.getLog(CommonUtils.class);

	private static final Random RANDOM = new Random();

	/**
	 * 자릿수만큼 랜덤숫자 생성 반환한다.
	 * 
	 * @author PCH
	 * @param loopCount 자릿수
	 * @return 자릿수만큼 랜덤숫자 생성 반환
	 */
	public static String getRandomNum(int loopCount) {
		String str = "";
		int d = 0;
		for (int i = 1; i <= loopCount; i++) {
			Random r = new Random();
			d = r.nextInt(9);
			str = str + Integer.toString(d);
		}
		return str;
	}

	private static final char[] chars;

	static {
		StringBuilder buffer = new StringBuilder();
		for (char ch = '0'; ch <= '9'; ++ch)
			buffer.append(ch);
		for (char ch = 'a'; ch <= 'z'; ++ch)
			buffer.append(ch);
		for (char ch = 'A'; ch <= 'Z'; ++ch)
			buffer.append(ch);
		chars = buffer.toString().toCharArray();
	}

	/**
	 * 자릿수만큼 랜덤 문자열(숫자포함) 생성 및 반환한다
	 * 
	 * @param length 자릿수
	 * @return 자릿수만큼 랜덤 문자열 반환
	 */
	public static String random(int length) {
		if (length < 1)
			throw new IllegalArgumentException("length < 1: " + length);

		StringBuilder randomString = new StringBuilder();
		Random random = new Random();

		for (int i = 0; i < length; i++) {
			randomString.append(chars[random.nextInt(chars.length)]);
		}
		return randomString.toString();
	}

	/** userId/sellerId 특수문자로 변경 */
	public static String convertEmail(String email) throws Exception {
		String str = "";
		int flag = email.indexOf('@');

		for (int i = 0; i < email.length(); i++) {
			if (i < 3) {
				str += email.charAt(i);
			} else {
				if (i < flag) {
					str += '*';
				} else if (i == flag) {
					str += '@';
				} else {
					str += email.charAt(i);
				}
			}
		}
		return str;
	}

	/**
	 * 비밀번호 암호화하는 메서드
	 * 
	 * @author PCH
	 * @param pw 인코딩 전의 비밀번호
	 * @return encodingPassword 인코딩 된 비밀번호
	 */
	public static String encode(String pw) {
		String encodingPassword = BCrypt.hashpw(pw, BCrypt.gensalt());
		return encodingPassword;

	}

	/**
	 * 사용자가 입력한 값과 암호화된 비밀번호가 맞는지 확인하는 메서드
	 * 
	 * @author PCH
	 * @param password       사용자가 입력한 비밀번호
	 * @param hashedPassword 암호화 되어있는 비밀번호
	 * @return true 일치, false 불일치
	 */
	public static Boolean chkPassword(String password, String hashedPassword) {
		if (StringUtils.isEmpty(hashedPassword)) { // 3rd part로그인 시 비밀번호가 없으므로 null point exception 피하기 위해 false값 리턴
			return false;
		} else {
			return BCrypt.checkpw(password, hashedPassword);
		}
	}

	/**
	 * 카테고리 아이디 자릿수로 카테고리 레벨을 반환한다.
	 * 1레벨 - 1~2자리
	 * 2레벨 - 4~5자리
	 * 3레벨 - 6~7자리
	 * 4레벨 - 8~9자리
	 */
	public static String getCategoryLevel(String categoryId) {
		String categoryLevel = "";
		int categoryIdLength = categoryId.length();
		if (categoryIdLength == 1 || categoryIdLength == 2) {
			categoryLevel = "1";
		} else if (categoryIdLength == 4 || categoryIdLength == 5) {
			categoryLevel = "2";
		} else if (categoryIdLength == 6 || categoryIdLength == 7) {
			categoryLevel = "3";
		} else if (categoryIdLength == 8 || categoryIdLength == 9) {
			categoryLevel = "4";
		}
		return categoryLevel;
	}

	/**
	 * URL을 생성해 준다.
	 * 
	 * @param url
	 * @param key
	 * @param value
	 * @return
	 */
	public static String getMakeUri(String uri, String key, String value) {
		String rtnUri = uri;

		if (StringUtils.isEmpty(uri))
			return "";

		try {
			// rtnUri = UrlBuilder.fromUri(new URI(uri)).setParameter(key,
			// value).toString();
		} catch (Exception e) {
			e.printStackTrace();
		}

		return rtnUri;
	}

	/**
	 * client ip 가져오기
	 * 
	 * @param request
	 * @return String ip
	 */
	public static String getClientIp(HttpServletRequest request) {

		request = ((ServletRequestAttributes) RequestContextHolder.currentRequestAttributes()).getRequest();

		String ip = request.getHeader("X-FORWARDED-FOR");

		if (ip == null) {
			ip = request.getRemoteAddr();
		}

		return ip;
	}

	/**
	 * 천단위 콤마 표시 반환
	 * 
	 * @param request
	 * @return String ip
	 */
	public static String getThousandComma(String strVal) {

		if (strVal == null || strVal.length() == 0)
			return "0";

		String strResult = strVal; // 출력할 결과를 저장할 변수
		Pattern p = Pattern.compile("(^[+-]?\\d+)(\\d{3})"); // 정규표현식
		Matcher regexMatcher = p.matcher(strVal);

		try {
			// int cnt = 0;
			while (regexMatcher.find()) {

				strResult = regexMatcher.replaceAll("$1,$2"); // 치환 : 그룹1 + "," + 그룹2

				// System.out.println("과정("+ (++cnt) +"):"+strResult);

				// 치환된 문자열로 다시 matcher객체 얻기
				// regexMatcher = p.matcher(strResult);
				regexMatcher.reset(strResult);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return strResult;
	}

	/**
	 * 이름 가운데 부분만 마스킹 처리 (앞1글자, 제일마지막 1글자는 제외)
	 * 
	 * @param name
	 * @return string
	 */
	public static String maskingName(String name) {

		if (StringUtils.isNotEmpty(name)) {
			StringBuffer sb = new StringBuffer();
			for (int i = 0; i < name.length(); i++) {
				String str = name.substring(i, i + 1);
				if (i == 0) {
					sb.append(str);
				} else if (i + 1 == name.length() && name.length() != 2) {
					sb.append(str);
				} else {
					sb.append("*");
				}
			}
			return sb.toString();
		} else {
			return name;
		}

	}

	/**
	 * 넘겨진 배열을 , 구분자로 한 문자열로 변경해서 리턴해주는 함수.
	 * 
	 * @author LSG
	 * @param array
	 * @return
	 */
	public static String arrayToString(String[] array) {
		String temp = "";
		for (int i = 0; i < array.length; i++) {
			temp += array[i] + ",";
		}
		temp = temp.substring(0, temp.length() - 1);

		return temp;
	}

	/**
	 * 넘겨진 문자열을 배열로 만들어주는 함수
	 * 
	 * @param str
	 * @author LSG
	 * @return
	 */
	public static String[] stringToArray(String str) {
		String[] temp = new String[0];
		if (str.indexOf(",") != -1) {
			temp = str.split(",");
		}

		return temp;
	}

	/**
	 * 넘겨진 파일빈을 수정 파일 빈으로 변환.
	 * 
	 * @param fileBean
	 * @author LSG
	 * @return
	 *         public static FileUploadBean chgBean(FileBean fileBean, String type,
	 *         String serverRootUrl) {
	 *         FileUploadBean fileUploadBean = new FileUploadBean();
	 *         if(fileBean instanceof BoardImgBean) { // 보드 게시판에서 파일을 등록했을 시 필요한 작업
	 *         fileUploadBean.setName(((BoardImgBean) fileBean).getImgOriginName());
	 *         fileUploadBean.setSize(((BoardImgBean) fileBean).getImgSize());
	 *         try {
	 *         String downUrl =
	 *         "/downloadFile?path="+URLEncoder.encode(((BoardImgBean)
	 *         fileBean).getImgPath() +"&type="+type, "UTF-8");
	 *         if( StringUtil.isNotEmpty(serverRootUrl) ) {
	 *         downUrl = serverRootUrl + downUrl;
	 *         }
	 *         fileUploadBean.setFile(downUrl);
	 *         fileUploadBean.setLocal(serverRootUrl + ((BoardImgBean)
	 *         fileBean).getImgPath());
	 *         fileUploadBean.setType(((BoardImgBean) fileBean).getContentType());
	 *         FileUploadSubBean subBean = new FileUploadSubBean();
	 *         subBean.setThumbnail(serverRootUrl + ((BoardImgBean)
	 *         fileBean).getImgPath());
	 *         subBean.setReaderCrossOrigin("anonymous");
	 *         subBean.setReaderForce(false);
	 *         subBean.setReaderSkip(false);
	 *         subBean.setUrl(serverRootUrl + ((BoardImgBean)
	 *         fileBean).getImgPath());
	 *         fileUploadBean.setData(subBean);
	 *         } catch (UnsupportedEncodingException e) {
	 *         // TODO Auto-generated catch block
	 *         e.printStackTrace();
	 *         }
	 *         }else {
	 *         if(fileBean != null) {
	 *         fileUploadBean.setName(fileBean.getFileOriginName());
	 *         fileUploadBean.setSize(fileBean.getFileSize());
	 * 
	 *         String downUrl;
	 *         try {
	 *         downUrl =
	 *         "/downloadFile?path="+URLEncoder.encode(fileBean.getOriginFilePath()+
	 *         fileBean.getFileName()+"&originName="+fileBean.getFileOriginName() +
	 *         "&type="+type, "UTF-8");
	 *         if( StringUtil.isNotEmpty(serverRootUrl) ) {
	 *         downUrl = serverRootUrl + downUrl;
	 *         }
	 *         fileUploadBean.setFile(downUrl);
	 *         fileUploadBean.setLocal(fileBean.getFilePath()+
	 *         fileBean.getFileName());
	 *         fileUploadBean.setType(fileBean.getContentType());
	 *         FileUploadSubBean subBean = new FileUploadSubBean();
	 *         subBean.setThumbnail(fileBean.getFilePath()+ fileBean.getFileName());
	 *         subBean.setReaderCrossOrigin("anonymous");
	 *         subBean.setReaderForce(false);
	 *         subBean.setReaderSkip(false);
	 *         subBean.setUrl(fileBean.getFilePath()+ fileBean.getFileName());
	 *         fileUploadBean.setData(subBean);
	 *         } catch (UnsupportedEncodingException e) {
	 *         // TODO Auto-generated catch block
	 *         e.printStackTrace();
	 *         }
	 *         }
	 *         }
	 *         return fileUploadBean;
	 *         }
	 */

	/**
	 * 넘겨진 문자열을 listMap으로 변환해 주는 메서드
	 * 
	 * @param req
	 * @author LSG
	 * @return
	 */
	public static List<Map<String, Object>> stringToMap(String req) {
		ObjectMapper objectMapper = new ObjectMapper();
		List<Map<String, Object>> readValue = new ArrayList<Map<String, Object>>();
		try {
			if (StringUtils.isNotEmpty(req)) {
				readValue = objectMapper.readValue(req, new TypeReference<List<Map<String, Object>>>() {
				});
			}
		} catch (JsonParseException e) {
			e.printStackTrace();
		} catch (JsonMappingException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

		return readValue;
	}

	/**
	 * 넘겨진 파라미터를 파일 업로드 포지션에 맞게 가져오는 함수
	 * 
	 * @param paramMap
	 * @author LSG
	 * @return
	 * @throws Exception
	 */
	public static List<String> makeReqs(Map<String, String[]> paramMap, boolean alignYn) throws Exception {

		List<String> reqs = new ArrayList<String>();

		for (Iterator<String> it = paramMap.keySet().iterator(); it.hasNext();) {
			String k = it.next();
			if (k.startsWith(Constants.FILE_FORM_NAME)) {
				reqs.add(k);
			}
		}

		if (alignYn) { // 정렬여부가 true라면 정렬

			List<String> temp = reqs.stream().sorted((str, str1) -> str.replace(Constants.FILE_FORM_NAME, "")
					.compareTo(str1.replace(Constants.FILE_FORM_NAME, ""))).collect(Collectors.toList());
			;
			reqs = temp;
		}

		return reqs;
	}

	/**
	 * 넘겨진 파라미터로 변경된 리스트와 새로 등록할 리스트를 담은 맵 객체를 리턴한다.
	 * 해당 기능은 실제 파일 처리만을 담당한다. 파일 IO전용
	 * 나머지 디비 관련은 deleteMap 혹은 insert맵에 담긴 정보로 리턴받아서 처리하면 된다.
	 * API버전(페이미)
	 * 
	 * @author LSG
	 * @param req
	 * @param list
	 * @param request
	 * @param cnt
	 * @return map
	 *         @SuppressWarnings("unchecked")
	 *         public static Map<String, Object> makeFile(String reqName, String
	 *         req, Object obj, HttpServletRequest request, String path, String
	 *         serverUrl) {
	 *         ApplicationContext applicationContext = new
	 *         AnnotationConfigApplicationContext(WebMvcConfig.class);
	 *         FileManageUtil fileUtil =
	 *         applicationContext.getBean(FileManageUtil.class);
	 * 
	 *         Map<String, Object> map = new HashMap<String, Object>();
	 *         List<String> fileNameList = new ArrayList<String>(); // 비교대상 파일명 담을
	 *         리스트 선언
	 *         int flag = 0;
	 *         try {
	 *         List<FileBean> list = new ArrayList<FileBean>();
	 *         if(obj instanceof List) {
	 *         list = (List<FileBean>)obj;
	 *         }else {
	 *         list.add((FileBean)obj);
	 *         }
	 *         List<Map<String,Object>> listMap = stringToMap(req); // string,
	 *         string[] 로 된 값을 listmap으로 변환
	 *         for(int i=0; i<listMap.size(); i++) { // 넘겨진 파라미터 만큼 반복
	 *         String value = listMap.get(i).get("file").toString(); // 파일명 추출
	 *         if(value.startsWith("0:/")) { // 해당 문자로 시작한다면 새로 등록할 파일
	 *         value = value.replace("0:/",""); // 해당 파일명만 추출
	 *         fileNameList.add(value); // 비교대상 리스트에 넣는다.
	 *         flag++;
	 *         }else {
	 *         value = value.substring(value.lastIndexOf("/")+1); // 경로를 삭제한 파일명만 추출
	 *         for(int j=0; j<list.size();j++) {
	 *         if(list.get(j) instanceof BoardImgBean) { // 넘겨진 파일이 보드이미지라면 기존의
	 *         파일빈이랑 다르기 때문에 새로 세팅을 한다.
	 *         BoardImgBean file = (BoardImgBean)list.get(j);
	 *         String filePath = file.getImgPath();
	 *         filePath = filePath.substring(filePath.lastIndexOf("/")+1);
	 *         if(value.equals(filePath)) { // 보드이미지는 랜덤으로 만들어진 이름은 없고 원본 파일명만 있기
	 *         때문에 원본 파일명과 비교
	 *         ((FileBean)list.get(j)).setDeleteYn("N"); // 일치하면 지우면 안되는 삭제 여부 N으로
	 *         세팅
	 *         }
	 *         }else {
	 *         FileBean file = (FileBean)list.get(j); // 파일빈으로 변환
	 *         if(value.equals(file.getFileName())) { // 두개의 파일이 일치한다면
	 *         ((FileBean) list.get(j)).setDeleteYn("N"); // 삭제 여부를 N으로 세팅
	 *         }
	 *         }
	 *         }
	 *         }
	 *         }
	 * 
	 *         for(int i=0; i< list.size();i++) { // 넘겨진 디비에서 조회된 리스트의 수만큼 반복문을
	 *         돌린다.(지울 대상만 판단하므로 디비에 저장된 값 만큼만 돌리면 된다).
	 *         FileBean fileBean = (FileBean)list.get(i);
	 *         if(!"N".equals(fileBean.getDeleteYn())) { // 지워야 할 파일이 존재한다면
	 *         fileUtil.deleteFile(fileBean.getOriginFilePath() +
	 *         fileBean.getFileName(), serverUrl); // 경로상에서 파일 삭제
	 *         }
	 *         }
	 *         map.put("deleteMap", list);
	 *         List<FileBean> listFileBean = new ArrayList<FileBean>();
	 *         if(flag > 0) { // 등록할 파일이 있다면
	 *         fileNameList =
	 *         fileNameList.stream().distinct().collect(Collectors.toList()); // 한
	 *         파일 폼의 중복된 파일명은 올라올 수 없으니 중복 제거한다.
	 *         // 등록할 파일 빈 추출
	 *         listFileBean = fileUtil.handleFileUploadList(request, path,
	 *         fileNameList, reqName, serverUrl);
	 *         }
	 *         map.put("insertMap", listFileBean);
	 *         }catch (Exception e) {
	 *         e.printStackTrace();
	 *         }
	 *         return map;
	 *         }
	 * 
	 *         /**
	 *         넘겨진 파라미터로 변경된 리스트와 새로 등록할 리스트를 담은 맵 객체를 리턴한다.
	 *         해당 기능은 실제 파일 처리만을 담당한다. 파일 IO전용
	 *         나머지 디비 관련은 deleteMap 혹은 insert맵에 담긴 정보로 리턴받아서 처리하면 된다.
	 *         로컬버전 (네일팝)
	 * @param req
	 * @param list
	 * @param request
	 * @param cnt
	 * @return map
	 *         @SuppressWarnings("unchecked")
	 *         public static Map<String, Object> makeFile2(String reqName, String
	 *         req, Object obj,HttpServletRequest request, String rootPath, String
	 *         path , String nlmTltle , String uploadType) {
	 *         Map<String, Object> map = new HashMap<String, Object>();
	 *         List<String> fileNameList = new ArrayList<String>(); // 비교대상 파일명 담을
	 *         리스트 선언
	 *         int flag = 0;
	 *         try {
	 *         List<FileBean> list = new ArrayList<FileBean>();
	 *         if(obj instanceof List) {
	 *         list = (List<FileBean>)obj;
	 *         }else {
	 *         list.add((FileBean)obj);
	 *         }
	 *         List<Map<String,Object>> listMap = stringToMap(req); // string,
	 *         string[] 로 된 값을 listmap으로 변환
	 *         for(int i=0; i<listMap.size(); i++) { // 넘겨진 파라미터 만큼 반복
	 *         String value = listMap.get(i).get("file").toString(); // 파일명 추출
	 *         if(value.startsWith("0:/")) { // 해당 문자로 시작한다면 새로 등록할 파일
	 *         value = value.replace("0:/",""); // 해당 파일명만 추출
	 *         fileNameList.add(value); // 비교대상 리스트에 넣는다.
	 *         flag++;
	 *         }else {
	 *         value = value.substring(value.lastIndexOf("/")+1); // 경로를 삭제한 파일명만 추출
	 *         for(int j=0; j<list.size();j++) {
	 *         if(list.get(j) instanceof BoardImgBean) { // 넘겨진 파일이 보드이미지라면 기존의
	 *         파일빈이랑 다르기 때문에 새로 세팅을 한다.
	 *         BoardImgBean file = (BoardImgBean)list.get(j);
	 *         String filePath = file.getImgPath();
	 *         filePath = filePath.substring(filePath.lastIndexOf("/")+1);
	 *         if(value.equals(filePath)) { // 보드이미지는 랜덤으로 만들어진 이름은 없고 원본 파일명만 있기
	 *         때문에 원본 파일명과 비교
	 *         ((FileBean)list.get(j)).setDeleteYn("N"); // 일치하면 지우면 안되는 삭제 여부 N으로
	 *         세팅
	 *         }
	 *         }else {
	 *         FileBean file = (FileBean)list.get(j); // 파일빈으로 변환
	 *         if(value.equals(file.getFileName())) { // 두개의 파일이 일치한다면
	 *         ((FileBean) list.get(j)).setDeleteYn("N"); // 삭제 여부를 N으로 세팅
	 *         }
	 *         }
	 *         }
	 *         }
	 *         }
	 * 
	 *         for(int i=0; i< list.size();i++) { // 넘겨진 디비에서 조회된 리스트의 수만큼 반복문을
	 *         돌린다.(지울 대상만 판단하므로 디비에 저장된 값 만큼만 돌리면 된다).
	 *         FileBean fileBean = (FileBean)list.get(i);
	 *         if(!"N".equals(fileBean.getDeleteYn())) { // 지워야 할 파일이 존재한다면
	 *         FileManagementLocalController.deleteFile(rootPath +
	 *         fileBean.getOriginFilePath() + fileBean.getFileName()); // 경로상에서 파일
	 *         삭제
	 *         }
	 *         }
	 *         map.put("deleteMap", list);
	 *         List<FileBean> listFileBean = new ArrayList<FileBean>();
	 *         if(flag > 0) { // 등록할 파일이 있다면
	 *         fileNameList =
	 *         fileNameList.stream().distinct().collect(Collectors.toList()); // 한
	 *         파일 폼의 중복된 파일명은 올라올 수 없으니 중복 제거한다.
	 *         // 등록할 파일 빈 추출
	 *         listFileBean =
	 *         FileManagementLocalController.handleFileUploadListVarLook(request,
	 *         rootPath, path, fileNameList, reqName , nlmTltle , uploadType);
	 *         }
	 *         map.put("insertMap", listFileBean);
	 *         }catch (Exception e) {
	 *         e.printStackTrace();
	 *         }
	 *         return map;
	 *         }
	 * 
	 * 
	 * 
	 *         /**
	 *         넘겨진 파일빈 리스트의 가장 큰 파일 타입을 가져온다.
	 * @param list
	 * @author LSG
	 * @return
	 * @throws Exception
	 *                   public static int getListMaxFileType(List<?> list) throws
	 *                   Exception{
	 *                   @SuppressWarnings("unchecked")
	 *                   List<FileBean> tempList = (List<FileBean>) list;
	 *                   return
	 *                   tempList.stream().map(FileBean::getFileType).map(Integer::parseInt).max(Integer::compare).get();
	 *                   }
	 */

	/**
	 * 날짜 비교 후 일(Day) 차이 출력
	 * 
	 * @param date
	 * @param newIconTerm
	 * @return boolean
	 */
	public static boolean newIconCheckByDate(String date, int newIconTerm) {
		// 현재 시간
		LocalDateTime nowDate = LocalDateTime.now();
		int result = (int) Duration
				.between(LocalDateTime.parse(date, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")), nowDate)
				.toDays();

		if (result <= newIconTerm) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * 넘겨진 리스트를 listMap으로 바꿔주는 함수
	 * 
	 * @param list
	 * @author LSG
	 * @return
	 */
	public static List<Map<String, Object>> voToMap(List<?> list) {
		List<Map<String, Object>> listMap = new ArrayList<Map<String, Object>>();
		try {
			for (int i = 0; i < list.size(); i++) {
				Map<String, Object> map = new LinkedHashMap<String, Object>(); // 순서에 맞춰야 하므로 linkedmap선언
				for (Field field : list.get(i).getClass().getDeclaredFields()) { // 해당 vo의 선언된 필드들을 전부 가져온다.
					field.setAccessible(true); // 해당 필드를 접근할 수 있게
					Object value = field.get(list.get(i)); // 해당 필드의 저장된 값을 가져온다.
					map.put(field.getName(), value); // 해당 필드의 이름과 값을 맵에 담는다.
				}
				listMap.add(map);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		return listMap;
	}

	/**
	 * 넘겨진 VO객체를 map으로 변경하는 함수
	 * 
	 * @param obj
	 * @author LSG
	 * @return
	 */
	public static Map<String, Object> voToMap(Object obj) {
		Map<String, Object> map = new LinkedHashMap<String, Object>();
		try {
			for (Field field : obj.getClass().getDeclaredFields()) {
				field.setAccessible(true);
				Object value = field.get(obj);
				map.put(field.getName(), value);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return map;
	}

	/**
	 * 맵에서 해당 키값 추출하는 메서드
	 * 
	 * @author LSG
	 */
	public static String[] getKeys(Map<String, Object> map) {
		return getKeys(map, false);
	}

	/**
	 * 맵에서 해당 키값 추출하는 메서드
	 * 
	 * @author LSG
	 */
	public static String[] getKeys(Map<String, Object> map, boolean b_sort) {
		Set<String> keySet = map.keySet();
		String[] keys = new String[keySet.size()];
		keySet.toArray(keys);
		if (b_sort)
			Arrays.sort(keys);
		return keys;
	}

	/**
	 * 다운로드 url을 만들어 주는 메서드
	 * 
	 * @param path
	 * @param type
	 * @author LSG
	 * @return
	 */
	public static String makeDownUrl(String path, String type) {
		String url = "/downloadFile?path=" + path + "&type=" + type;
		if (url.indexOf("\\\\") != -1) {
			url = url.replaceAll("\\\\", "/");
		}
		return url;
	}

	/**
	 * 넘어온 객체를 스트링 객체로 변환시켜주는 메서드
	 * 
	 * @param obj
	 * @author LSG
	 * @return
	 */
	public static String toString(Object obj) {
		String data = null;

		if (obj instanceof Integer) {

			data = Integer.toString((int) obj);

		} else if (obj instanceof String) {

			data = obj.toString();

		} else if (obj instanceof Double) {

			data = Double.toString((double) obj);

		} else if (obj == null) {

			data = "";

		}
		return data;
	}

	/**
	 * multipart 파일을 일반 file로 변환
	 * 
	 * @param file
	 * @author LSG
	 * @return
	 */
	public static File multipartToFile(MultipartFile multipart) throws IllegalStateException, IOException {

		File convFile = new File(multipart.getOriginalFilename());

		multipart.transferTo(convFile);

		return convFile;
	}

	/**
	 * 부호에 대한 처리가 추가된 int 변환함수
	 * <p>
	 * 
	 * @param str 소스 문자열
	 * @author LSG
	 * @return 변환된 int 값
	 */
	public static int to_int(String str) {
		if (str == null || str.length() == 0)
			return 0;

		String nstr = "";
		String chars = "-0123456789";

		for (int i = 0; i < str.length(); i++) {
			if (chars.indexOf(str.charAt(i)) != -1)
				nstr += str.charAt(i);
		}

		if (nstr.length() == 0)
			return 0;

		int sign = 1;

		if (nstr.indexOf("-") >= 0) {
			sign = -1;
			nstr = nstr.substring(nstr.indexOf("-") + 1);

			if (nstr.length() == 0)
				return 0;
		}

		return sign * Integer.parseInt(nstr);
	}

	/**
	 * 부호에 대한 처리가 추가된 long 변환함수
	 * <p>
	 * 
	 * @param str 소스 문자열
	 * @return 변환된 long 값
	 */
	public static long to_long(String str) {
		if (str == null || str.length() == 0)
			return 0;

		String nstr = "";
		String chars = "-0123456789";

		for (int i = 0; i < str.length(); i++) {
			if (chars.indexOf(str.charAt(i)) != -1)
				nstr += str.charAt(i);
		}

		if (nstr.length() == 0)
			return 0;

		int sign = 1;

		if (nstr.indexOf("-") >= 0) {
			sign = -1;
			nstr = nstr.substring(nstr.indexOf("-") + 1);

			if (nstr.length() == 0)
				return 0;
		}

		return sign * Long.parseLong(nstr);
	}

	/**
	 * 부호에 대한 처리가 추가된 float 변환함수
	 * <p>
	 * 
	 * @param str 소스 문자열
	 * @author LSG
	 * @return 변환된 float 값
	 */
	public static float to_float(String str) {
		if (str == null)
			return 0;

		str = trim(str);

		if (str.length() == 0)
			return 0;

		int sign = 1;

		if (str.indexOf("-") >= 0) {
			sign = -1;
			str = str.substring(str.indexOf("-") + 1);
		}

		return sign * Float.parseFloat(str);
	}

	/**
	 * 확장문자 공백에 대한 처리가 추가된 trim 함수
	 * <p>
	 * 
	 * @param str 소스 문자열
	 * @author LSG
	 * @return trim 처리된 문자열
	 */
	public static String trim(String str) {
		if (str == null)
			return null;

		str = replace(str, "　", "  ");

		return str.trim();
	}

	/**
	 * 문자열 단위 치환(String.replace는 char단위 치환)
	 * <p>
	 * 
	 * @param str     소스 문자열
	 * @param pattern 찾을 문자열
	 * @param replace 바꿀 문자열
	 * @author LSG
	 * @return 치환된 문자열
	 */
	public static String replace(String str, String pattern, String replace) {

		if (str == null || str.length() < 1)
			return "";

		int s = 0;
		int e = 0;

		StringBuffer result = new StringBuffer();

		while ((e = str.indexOf(pattern, s)) >= 0) {
			result.append(str.substring(s, e));
			result.append(replace);
			s = e + pattern.length();
		}

		result.append(str.substring(s));

		return result.toString();
	}

	/**
	 * 문자열 기본 값 가져오는 함수
	 * 
	 * @param obj
	 * @param defaultVal
	 * @author LSG
	 * @return
	 */
	public static String getDefault(Object obj, String defaultVal) {
		String rtnVal = (String) obj;
		if (null == rtnVal) {
			rtnVal = getDefault(defaultVal, "");
		}
		return rtnVal;
	}

	/**
	 * 숫자 기본값 가져오는 함수
	 * 
	 * @param obj
	 * @param defaultVal
	 * @return
	 */
	public static int getDefault(Object obj, int defaultVal) {
		int rtnVal = 0;
		if (obj == null) {
			rtnVal = getDefault(defaultVal, 0);
		} else {
			rtnVal = (int) obj;
		}
		return rtnVal;
	}

	/**
	 * 푸쉬, 이벤트, 메일, sms 동의 여부에 따른 Map (true or false)
	 * 
	 * @param userBean
	 * @return
	 */
	/*
	 * public static Map<String, Boolean> getConsent(UserBean userBean) {
	 * 
	 * Map<String, Boolean> map = new HashMap<String, Boolean>();
	 * 
	 * String status = userBean.getNotiStatusYn(); String event =
	 * userBean.getNotiEventYn(); String mail = userBean.getNotiMailYn(); String sms
	 * = userBean.getNotiSmsYn();
	 * 
	 * map.put("status", userBean == null ? false : isTrueFalse(status));
	 * map.put("event", userBean == null ? false : isTrueFalse(event));
	 * map.put("mail", userBean == null ? false : isTrueFalse(mail)); map.put("sms",
	 * userBean == null ? false : isTrueFalse(sms));
	 * 
	 * return map; }
	 */

	/**
	 * YN에 따른 true false 리턴
	 * 
	 * @param yn
	 * @return
	 */
	private static boolean isTrueFalse(String yn) {

		if ("Y".equals(yn)) {
			return true;
		} else {
			return false;
		}
	}

	/**
	 * StackTrace 정보를 문자열로 반환한다.
	 * 
	 * @param Thrwable t
	 * @return String
	 */
	public static String getStackTrace2Str(Throwable t) {
		StringWriter sw = new StringWriter();
		t.printStackTrace(new PrintWriter(sw));
		return sw.toString();
	}

	/**
	 * 네일팝 관리자 권한 변경하기
	 * 
	 * @param String authList
	 * @return String
	 */
	public static String authListCodeToString(String authList) {
		String[] authArr = authList.split(",");
		String resultAuth = "";
		for (int i = 0; i < authArr.length; i++) {
			switch (authArr[i]) {
				case "AR_1":
					resultAuth += "회원 관리 / ";
					break;

				case "AR_2":
					resultAuth += "컨텐츠 관리 / ";
					break;

				case "AR_3":
					resultAuth += "시스템 관리 / ";
					break;

				case "AR_4":
					resultAuth += "통계 분석 / ";
					break;

				case "AR_5":
					resultAuth += "관리자 권한 / ";
					break;
			}
		}
		resultAuth = resultAuth.substring(0, resultAuth.length() - 2);
		return resultAuth;
	}

	public static boolean byteCheck(String txt, int standardByte) {
		if (StringUtils.isEmpty(txt)) {
			return true;
		}

		// 바이트 체크 (영문 1, 한글 2, 특문 1)
		int en = 0;
		int ko = 0;
		int etc = 0;

		char[] txtChar = txt.toCharArray();
		for (int j = 0; j < txtChar.length; j++) {
			if (txtChar[j] >= 'A' && txtChar[j] <= 'z') {
				en++;
			} else if (txtChar[j] >= '\uAC00' && txtChar[j] <= '\uD7A3') {
				ko++;
				ko++;
			} else {
				etc++;
			}
		}

		int txtByte = en + ko + etc;
		if (txtByte > standardByte) {
			return false;
		} else {
			return true;
		}

	}

	/**
	 * 주문 번호 생성
	 * - 년(4자리)+월(2자리)+일(2자리)+시(2자리)+분(2자리)+초(2자리)+밀리세컨(3자리) = 총 17자리
	 * - 서버별 중복을 피하기 위해 서버아이디(1자리)를 마지막에 추가한다.
	 */
	public static synchronized String getOrderId() throws Exception {
		SimpleDateFormat formatter = new SimpleDateFormat("yyyyMMddHHmmssSSS", Locale.KOREA);
		Date currentTime = new Date();
		// String dTime = formatter.format ( currentTime )+SERVER_ID;
		String dTime = formatter.format(currentTime);
		return dTime;
	}

	/**
	 * 64자리 oid 생성
	 * 
	 * @return
	 * @throws Exception
	 */
	public static synchronized String getOrderId64() throws Exception {
		SimpleDateFormat formatter = new SimpleDateFormat("yyyyMMddHHmmssSSS", Locale.KOREA);
		Date currentTime = new Date();
		// String dTime = formatter.format ( currentTime )+SERVER_ID;
		String dTime = formatter.format(currentTime);

		int length = 47;
		boolean useLetters = true;
		boolean useNumbers = false;
		String generatedString = RandomStringUtils.random(length, useLetters, useNumbers);

		return dTime + generatedString;
	}

	// Generate a random 4-digit number
	public static int generateRandomNumber() throws Exception {
		return RANDOM.nextInt(9000) + 1000; // This ensures the number is always 4 digits
	}

	// Generate a random 4-letter string
	public static String generateRandomString() throws Exception {
		char[] chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();
		StringBuilder sb = new StringBuilder(4);
		for (int i = 0; i < 4; i++) {
			char c = chars[RANDOM.nextInt(chars.length)];
			sb.append(c);
		}
		return sb.toString();
	}

	// Generate app deep link URL
	@SuppressWarnings("deprecation")
	public static String generateAppDeepLinkUrl(String appwebUrl, String destinePage) throws Exception {
		final String DEEP_LINK_BASE_URL = "https://leit1.page.link/?ibi=kr.co.leit.app&isi=6467376048&apn=kr.co.leit.app&link=";
		final String LEIT_HOMEPAGE_URL = "https://le-it.com?link=";

		return DEEP_LINK_BASE_URL + URLEncoder.encode(LEIT_HOMEPAGE_URL + appwebUrl + destinePage);
	}

	public static String getReferer(String ROOT, HttpServletRequest request) {
		String referer = "";
		try {
			URL url = new URL(request.getRequestURL().toString());

			if (ROOT.equals("real")) {
				String host = url.getHost();

				referer = "https://" + host;
			} else {
				String host = url.getHost();
				int port = url.getPort();

				if (host.contains("leit-api.aniss.co.kr/")) {
					referer = "http://" + host;
				} else {
					referer = "http://" + host + ":" + port;
				}
			}
		} catch (MalformedURLException e) {
			referer = "http://localhost:8098";
		}

		return referer;
	}

	// 자바빈 to HashMap
	public static Map<String, Object> objectToMap(Object obj, boolean isLower, List<String> replaceKeyList)
			throws IllegalAccessException {
		if (obj == null) {
			return new HashMap<>();
		}

		Map<String, Object> map = new HashMap<>();
		Class<?> clazz = obj.getClass();

		for (Field field : clazz.getDeclaredFields()) {
			field.setAccessible(true);
			Object value = field.get(obj);

			if (value == null) {
				// Handle null value
				String fieldName = processFieldName(field.getName(), isLower, replaceKeyList);
				map.put(fieldName, null);
				continue;
			}

			String fieldName = processFieldName(field.getName(), isLower, replaceKeyList);

			if (value instanceof Object[] || value instanceof List) {
				// Field is an array or a list, convert each element to a map if it's an object
				List<Object> listValue = new ArrayList<>();
				for (Object element : (Iterable<?>) value) {
					if (element instanceof Map) {
						listValue.add(element);
					} else {
						listValue.add(objectToMap(element, isLower, replaceKeyList));
					}
				}
				map.put(fieldName, listValue);
			} else if (value instanceof Map) {
				map.put(fieldName, value);
			} else if (value instanceof Object && !isPrimitiveOrWrapper(value)) {
				map.put(fieldName, objectToMap(value, isLower, replaceKeyList));
			} else {
				map.put(fieldName, value);
			}
		}
		return map;
	}

	private static String processFieldName(String fieldName, boolean isLower, List<String> replaceKeyList) {
		// Convert fieldName to lower case if isLower is true
		String processedFieldName = isLower ? fieldName.toLowerCase() : fieldName;

		if (replaceKeyList != null && replaceKeyList.size() > 0) {
			// Try to find a direct match in the replaceKeyList first
			for (String replaceKey : replaceKeyList) {
				if (replaceKey.replace("_", "").equalsIgnoreCase(processedFieldName)) {
					processedFieldName = replaceKey;
					return replaceKey;
				}
			}
		}

		// Return the field name as is if no match is found
		return processedFieldName;
	}

	private static boolean isPrimitiveOrWrapper(Object obj) {
		return obj instanceof Long || obj instanceof Integer || obj instanceof Double ||
				obj instanceof Float || obj instanceof Boolean || obj instanceof Character ||
				obj instanceof Byte || obj instanceof Short || obj instanceof String ||
				obj instanceof Date; // Add more types as necessary
	}

	// xml to HashMap
	public static Map<String, Object> xmlToMap(String xmlString)
			throws IllegalAccessException, ParserConfigurationException, SAXException, IOException {
		if (xmlString == null || xmlString.length() == 0) {
			return new HashMap<>();
		}

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();
		Document document = builder.parse(new ByteArrayInputStream(xmlString.getBytes()));

		Element root = document.getDocumentElement();
		NodeList nodeList = root.getChildNodes();

		Map<String, Object> xmlResult = new HashMap<String, Object>();
		for (int i = 0; i < nodeList.getLength(); i++) {
			Node node = nodeList.item(i);
			if (node.getNodeType() == Node.ELEMENT_NODE) {
				if (xmlResult.containsKey(node.getNodeName())) {
					Object value = node.getTextContent();

					// Map<String, Object> subNode = new HashMap<String, Object>();
					if (xmlResult.get(node.getNodeName()) instanceof List) {
						@SuppressWarnings("unchecked")
						List<Object> previousValueList = (List) xmlResult.get(node.getNodeName());

						// subNode.put(xmlString, value);
						previousValueList.add(value);

						xmlResult.put(node.getNodeName(), previousValueList);
					} else {
						List<Object> newValueList = new ArrayList<Object>();

						newValueList.add(xmlResult.get(node.getNodeName()));
						newValueList.add(value);

						xmlResult.put(node.getNodeName(), newValueList);
					}
				} else {
					xmlResult.put(node.getNodeName(), node.getTextContent());
				}
			}
		}
		return xmlResult;
	}

	public static String nvl(String str, String defaultString) {
		return str == null ? defaultString : str;
	}

	/**
	 * properties 파일 처리
	 */
	public static Properties readProperties(Class cls, String propFileName) {
		Properties prop = new Properties();
		InputStream inputStream = cls.getClassLoader().getResourceAsStream(propFileName);

		try {
			if (inputStream != null) {
				prop.load(inputStream);
				return prop;
			} else {
				throw new FileNotFoundException("프로퍼티 파일 '" + propFileName + "'을 resource에서 찾을 수 없습니다.");
			}
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

}