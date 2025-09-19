package fwj.aniss.api.common.utils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import com.google.gson.Gson;

public class HttpConnectionUtil {

    /**
     * @param pURL          : 요청 URL
     * @param pList         : 파라미터 객체 (HashMap<String,String>)
     * @param reqProperties : 요청 헤더
     * @param formData      : 요청 Body
     */
    public static String postRequest(String pURL, HashMap<String, String> reqPropertie,
            HashMap<String, String> formData) {
        return request(pURL, "POST", reqPropertie, formData, "UTF-8", "UTF-8");
    }

    /**
     * @param pURL          : 요청 URL
     * @param pList         : 파라미터 객체 (HashMap<String,String>)
     * @param reqProperties : 요청 헤더
     * @param formData      : 요청 Body
     */
    public static String request(String pURL, String method, HashMap<String, String> reqPropertie,
            HashMap<String, String> formData, String reqCharset, String respCharset) {

        String myResult = "";

        try {
            // URL 설정하고 접속하기
            URL url = new URL(pURL); // URL 설정

            HttpURLConnection http = (HttpURLConnection) url.openConnection(); // 접속
            // --------------------------
            // 전송 모드 설정 - 기본적인 설정
            // --------------------------
            http.setDefaultUseCaches(false);
            http.setDoInput(true); // 서버에서 읽기 모드 지정
            http.setDoOutput(true); // 서버로 쓰기 모드 지정
            http.setRequestMethod(method); // 전송 방식은 POST, GET

            // --------------------------
            // 헤더 세팅
            // --------------------------
            // 서버에게 웹에서 <Form>으로 값이 넘어온 것과 같은 방식으로 처리하라는 걸 알려준다
            if (reqPropertie != null) {
                Iterator<Entry<String, String>> iters = reqPropertie.entrySet().iterator();
                while (iters.hasNext()) {
                    Map.Entry<String, String> entry = iters.next();
                    String key = entry.getKey();
                    String val = entry.getValue();
                    http.setRequestProperty(key, val); // "content-type", "application/x-www-form-urlencoded"
                }
            } else {
                http.setRequestProperty("content-type", "application/x-www-form-urlencoded");
            }

            // --------------------------
            // 서버로 값 전송
            // --------------------------
            StringBuffer buffer = new StringBuffer();

            // HashMap으로 전달받은 파라미터가 null이 아닌경우 버퍼에 넣어준다
            if (formData != null) {
                Gson gson = new Gson();
                String jsonStr = gson.toJson(formData);
                System.out.println("reqeust form data json ===>" + jsonStr);
                buffer.append(jsonStr);
            }

            try (OutputStream os = http.getOutputStream()) {
                byte request_data[] = buffer.toString().getBytes(respCharset);
                os.write(request_data);
                os.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

            http.connect();

            // --------------------------
            // Response Code
            // --------------------------
            // http.getResponseCode();

            // --------------------------
            // 서버에서 header 전송받기
            // --------------------------
            /**
             * System.out.println("Response header ===>");
             * Map<String, List<String>> headerFields = http.getHeaderFields();
             * for (Map.Entry<String, List<String>> entry : headerFields.entrySet()) {
             * String headerName = entry.getKey();
             * List<String> headerValues = entry.getValue();
             * 
             * System.out.println("Header Name: " + headerName);
             * for (String value : headerValues) {
             * System.out.println("Header Value: " + value);
             * }
             * }
             **/
            // key 값으로 바로 취득도 가능
            // String contentType = http.getHeaderField("Content-Type");
            // System.out.println("Content-Type: " + content

            // --------------------------
            // 서버에서 Body 전송받기
            // --------------------------
            // System.out.println("Response body ===>");
            InputStreamReader tmp = new InputStreamReader(http.getInputStream(), respCharset);
            BufferedReader reader = new BufferedReader(tmp);
            StringBuilder builder = new StringBuilder();
            String str;
            while ((str = reader.readLine()) != null) {
                builder.append(str + "\n");
            }
            myResult = builder.toString();
            return myResult;

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return myResult;
    }

    /**
     * @param pURL          : 요청 URL
     * @param pList         : 파라미터 객체 (HashMap<String,String>)
     * @param reqProperties : 요청 헤더
     */
    public static String getRequest(String pURL, HashMap<String, String> reqPropertie, HashMap<String, String> pList) {
        return getRequest(pURL, reqPropertie, pList, "UTF-8", "UTF-8");
    }

    public static String getRequest(String pURL, HashMap<String, String> reqPropertie, HashMap<String, String> pList,
            String reqCharset, String respCharset) {

        String myResult = "";
        StringBuffer buffer = new StringBuffer();

        try {
            // HashMap으로 전달받은 파라미터가 null이 아닌경우 버퍼에 넣어준다
            if (pList != null) {

                Set<String> key = pList.keySet();
                int counter = 0;
                for (Iterator<String> iterator = key.iterator(); iterator.hasNext();) {
                    String keyName = (String) iterator.next();
                    String valueName = pList.get(keyName);
                    if (counter == 0) {
                        buffer.append("?").append(keyName).append("=").append(valueName); // "?key=value"
                    } else {
                        buffer.append("&").append(keyName).append("=").append(valueName);
                    }
                    counter++;
                }
            }

            // URL 설정하고 접속하기
            URL url = new URL(pURL + buffer.toString()); // URL 설정

            HttpURLConnection http = (HttpURLConnection) url.openConnection(); // 접속
            // --------------------------
            // 전송 모드 설정 - 기본적인 설정
            // --------------------------
            http.setDefaultUseCaches(false);
            http.setConnectTimeout(20000); // 서버에 연결되는 Timeout 시간 설정
            http.setReadTimeout(20000); // InputStream 읽어 오는 Timeout 시간 설정
            http.setRequestProperty("Content-Type", "application/json");
            http.setRequestProperty("Transfer-Encoding", "chunked");
            http.setRequestProperty("Connection", "keep-alive");
            http.setDoOutput(false); // 서버로 쓰기 모드 지정
            http.setRequestMethod("GET"); // 전송 방식은 get

            // --------------------------
            // 헤더 세팅
            // --------------------------
            // 서버에게 웹에서 <Form>으로 값이 넘어온 것과 같은 방식으로 처리하라는 걸 알려준다
            if (reqPropertie != null) {
                Iterator<Entry<String, String>> iters = reqPropertie.entrySet().iterator();
                while (iters.hasNext()) {
                    Map.Entry<String, String> entry = iters.next();
                    String key = entry.getKey();
                    String val = entry.getValue();
                    http.setRequestProperty(key, val); // "content-type", "application/x-www-form-urlencoded"
                }
            } else {
                http.setRequestProperty("content-type", "application/x-www-form-urlencoded");
            }

            http.connect();

            // --------------------------
            // Response Code
            // --------------------------
            // http.getResponseCode();

            // --------------------------
            // 서버에서 header 전송받기
            // --------------------------
            /**
             * System.out.println("Response header ===>");
             * Map<String, List<String>> headerFields = http.getHeaderFields();
             * for (Map.Entry<String, List<String>> entry : headerFields.entrySet()) {
             * String headerName = entry.getKey();
             * List<String> headerValues = entry.getValue();
             * 
             * System.out.println("Header Name: " + headerName);
             * for (String value : headerValues) {
             * System.out.println("Header Value: " + value);
             * }
             * }
             **/
            // key 값으로 바로 취득도 가능
            // String contentType = http.getHeaderField("Content-Type");
            // System.out.println("Content-Type: " + content

            // --------------------------
            // 서버에서 Body 전송받기
            // --------------------------
            // System.out.println("Response body ===>");
            InputStreamReader tmp = new InputStreamReader(http.getInputStream(), respCharset);
            BufferedReader reader = new BufferedReader(tmp);
            StringBuilder builder = new StringBuilder();
            String str;
            while ((str = reader.readLine()) != null) {
                builder.append(str + "\n");
            }
            myResult = builder.toString();
            return myResult;

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        return myResult;
    }

}
