// package kis.stock.aniss.common.controller.auth;

// import java.util.HashMap;
// import java.util.List;
// import java.util.Map;

// import org.apache.commons.lang3.StringUtils;
// import org.springframework.beans.factory.annotation.Autowired;
// import org.springframework.beans.factory.annotation.Value;
// import org.springframework.web.bind.annotation.GetMapping;
// import org.springframework.web.bind.annotation.PostMapping;
// import org.springframework.web.bind.annotation.RequestBody;
// import org.springframework.web.bind.annotation.RequestMapping;
// import org.springframework.web.bind.annotation.RequestParam;
// import org.springframework.web.bind.annotation.RestController;

// import com.google.gson.Gson;

// import io.jsonwebtoken.Claims;
// import jakarta.servlet.http.HttpServletRequest;
// import jakarta.servlet.http.HttpServletResponse;
// import kis.stock.aniss.common.bean.member.MemberBean;
// import kis.stock.aniss.common.bean.strategy.StrategyBean;
// import kis.stock.aniss.common.bean.strategy.StrategyStockSwitchBean;
// import kis.stock.aniss.common.constants.Constants;
// import kis.stock.aniss.common.exception.CommonException;
// import kis.stock.aniss.common.service.kis.rest.AccessTokenManager;
// import kis.stock.aniss.common.service.member.MemberService;
// import kis.stock.aniss.common.service.strategy.StrategyService;
// import kis.stock.aniss.common.utils.CommonUtils;
// import kis.stock.aniss.common.utils.JwtTokenHelper;
// import kis.stock.aniss.common.utils.ResUtils;
// // import kis.stock.aniss.stragegy.itbong.launcher.A04Launcher;
// // import kis.stock.aniss.stragegy.itbong.scheduler.A03StrategryScheduler;
// // import kis.stock.aniss.stragegy.itbong.scheduler.A05StrategryScheduler;
// import lombok.extern.slf4j.Slf4j;

// @Slf4j
// @RestController
// @RequiredArgsConstructor
// @RequestMapping(value="/auth")
// public class AuthController {

// @Autowired
// private MemberService memberService;

// @Autowired
// private StrategyService strategyService;

// @Autowired
// private Gson gson;

// @Autowired
// private AccessTokenManager accessTokenManager;

// // @Autowired
// // private A04Launcher a04Launcher;

// @Value("${member.id}")
// private String MEMBER_ID;

// /**
// * 로그인
// * @param memberId/password
// */
// @PostMapping(value = "/doLogin")
// public Map<String, Object> doLogin(@RequestBody MemberBean loginInfo,
// HttpServletRequest request) throws Exception{
// Map<String, Object> result = new HashMap<>();

// if(StringUtils.isEmpty(loginInfo.getLoginId()) ||
// StringUtils.isEmpty(loginInfo.getPassword())) {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), "ID 혹은
// 패스워드 없음");
// }

// MemberBean member = memberService.selectMemberInfo(loginInfo);
// if(member != null) {
// if(CommonUtils.chkPassword(loginInfo.getPassword(), member.getPassword())) {

// memberService.updateLoginDate(member.getMemberNo());

// String issuer = Long.toString(member.getMemberNo());
// String id = member.getMemberId();
// String subject = gson.toJson(member);
// String authToken = JwtTokenHelper.createAdminJWT(
// id+"",
// issuer,
// subject);
// member.setPassword(null);
// result.put("memberInfo", member);
// result.put("authToken", authToken);

// accessTokenManager.storeMember(member.getMemberId(), member);
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// result);
// }
// else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), "비밀번호
// 일치하지 않음");
// }
// }
// else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), "로그인 유저
// 정보 없음");
// }
// }

// @PostMapping(value = "/deleteMemberNew")
// public Map<String, Object> deleteMember(@RequestBody MemberBean member,
// HttpServletRequest request) throws Exception{
// int res = memberService.deleteMember(member);
// if( res > 0 ) {
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// null);
// } else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), null);
// }
// }

// //토큰 검증
// @PostMapping(value = "/verifyToken")
// public Map<String, Object> verifyToken(HttpServletRequest request,
// HttpServletResponse response) throws Exception {
// Map<String, Object> map = new HashMap<String, Object>();
// String result = Constants.RESULT_VAL_FAIL;
// String resultMsg = "회원정보 Token 검증에 실패 하였습니다.";

// //헤더로 부터 넘어온 토큰을 검증한다.
// String authToken = request.getHeader("Authorization");
// log.info("authToken:" + authToken);

// //토큰이 존재한다면 토큰값이 유효한지를 체크한다.
// if(authToken != null) {
// authToken = authToken.replace("Bearer ", "");

// Claims claims = JwtTokenHelper.parseClaims(authToken).getBody();
// String id = claims.getId();
// String issuer = claims.getIssuer();
// String subject = claims.getSubject();
// log.info("id:" + id + ", isuuer:" + issuer + ", subejct:" + subject);
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// null);
// } else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), null);
// }

// }//end method

// //맴버 전략스위치
// @PostMapping(value = "/turnStrategySwitchOnOff")
// public Map<String, Object>
// turnStrategySwitchOnOff(@RequestParam(value="memberId", required=true) String
// memberId,
// @RequestParam(value="strategyId", required=true) String strategyId,
// @RequestParam(value="buySwitchBtn", required=false) String buySwitchBtn,
// @RequestParam(value="sellSwitchBtn", required=false) String sellSwitchBtn,
// HttpServletRequest request,
// HttpServletResponse response) throws Exception {
// int res = 0;

// if(StringUtils.isNotEmpty(buySwitchBtn)) {
// buySwitchBtn = buySwitchBtn.equals("Y") ? "ON" : "OFF";

// res = memberService.turnStrategySwitchOnOff(strategyId, memberId,
// buySwitchBtn, null);
// }

// if(StringUtils.isNotEmpty(sellSwitchBtn)) {
// sellSwitchBtn = sellSwitchBtn.equals("Y") ? "ON" : "OFF";

// res = memberService.turnStrategySwitchOnOff(strategyId, memberId, null,
// sellSwitchBtn);
// }

// //TODO 해당 전략이 ON/OFF 될때 전략의 static 변수를 교체해준다.
// StrategyBean stBean = new StrategyBean();
// stBean.setStrategyId(strategyId);
// StrategyBean strategyBean = strategyService.selectStrategyInfo(stBean);

// if( StringUtils.equals(MEMBER_ID, memberId) && "A03".equals(strategyId) ) {
// //전략의 ON, OFF 값을 DB로부터 읽어와서 셋팅한다.
// if(buySwitchBtn != null) {
// A03StrategryScheduler.IS_BUY_PROC_STOP = "ON".equals(buySwitchBtn) ? false :
// true;
// System.out.println("/turnStrategySwitchOnOff ===> buySwitchBtn: + " +
// buySwitchBtn + ", A03 IS_BUY_PROC_STOP:" +
// A03StrategryScheduler.IS_BUY_PROC_STOP);
// }
// if(sellSwitchBtn != null) {
// A03StrategryScheduler.IS_SELL_PROC_STOP = "ON".equals(sellSwitchBtn) ? false
// : true;
// System.out.println("/turnStrategySwitchOnOff ===> sellSwitchBtn: + " +
// sellSwitchBtn + ", A03 IS_SELL_PROC_STOP:" +
// A03StrategryScheduler.IS_SELL_PROC_STOP);
// }
// }
// else if( StringUtils.equals(MEMBER_ID, memberId) && "A04".equals(strategyId)
// ) {
// //전략의 ON, OFF 값을 DB로부터 읽어와서 셋팅한다.
// if(buySwitchBtn != null) {
// A04Launcher.IS_BUY_PROC_STOP = "ON".equals(buySwitchBtn) ? false : true;
// System.out.println("/turnStrategySwitchOnOff ===> buySwitchBtn: + " +
// buySwitchBtn + ", A04 IS_BUY_PROC_STOP:" + A04Launcher.IS_BUY_PROC_STOP);
// }
// if(sellSwitchBtn != null) {
// A04Launcher.IS_SELL_PROC_STOP = "ON".equals(sellSwitchBtn) ? false : true;
// System.out.println("/turnStrategySwitchOnOff ===> sellSwitchBtn: + " +
// sellSwitchBtn + ", A04 IS_SELL_PROC_STOP:" + A04Launcher.IS_SELL_PROC_STOP);
// }
// }
// else if( StringUtils.equals(MEMBER_ID, memberId) && "A05".equals(strategyId)
// ) {
// //전략의 ON, OFF 값을 DB로부터 읽어와서 셋팅한다.
// if(buySwitchBtn != null) {
// A05StrategryScheduler.IS_BUY_PROC_STOP = "ON".equals(buySwitchBtn) ? false :
// true;
// System.out.println("/turnStrategySwitchOnOff ===> buySwitchBtn: + " +
// buySwitchBtn + ", A05 IS_BUY_PROC_STOP:" +
// A05StrategryScheduler.IS_BUY_PROC_STOP);
// }
// if(sellSwitchBtn != null) {
// A05StrategryScheduler.IS_SELL_PROC_STOP = "ON".equals(sellSwitchBtn) ? false
// : true;
// System.out.println("/turnStrategySwitchOnOff ===> sellSwitchBtn: + " +
// sellSwitchBtn + ", A05 IS_SELL_PROC_STOP:" +
// A05StrategryScheduler.IS_SELL_PROC_STOP);
// }
// if(strategyBean != null) {
// //최대 투자금 설정
// A05StrategryScheduler.INIT_BUY_MAX_PRICE = strategyBean.getMaxInvest();

// //해당 전략의 설정들 가져오기
// List<StrategyStockSwitchBean> list =
// memberService.selectMemberStrategyStockSwitchList(stBean.getStrategyId(),
// stBean.getMemberId());
// for(StrategyStockSwitchBean bean : list) {

// // public static double PROFIT_FULL_SELL_RATE = 1.2; //이익율 비율
// // public static double LOSS_FULL_SELL_RATE = -0.4; //손절 비율
// // public static int MAX_YESTER_VOLUE_RATE = 500; //전일대비 거래량 300%
// // public static int DAY_MAX_BUY_COUNT = 3; //하루 최대 매수횟수
// // public static double BUY_DECRESE_RATE = 3.0; //매수전 현재가보다 3% 낮은 가격으로 매수하기
// 위한 수치

// //이익율 비율
// // A05StrategryScheduler.PROFIT_FULL_SELL_RATE = Double.parseDouble(
// bean.getVal1() );
// // //손절 비율
// // A05StrategryScheduler.LOSS_FULL_SELL_RATE = Double.parseDouble(
// bean.getVal2() );
// // //전일대비 거래량 300%
// // A05StrategryScheduler.MAX_YESTER_VOLUE_RATE = Integer.parseInt(
// bean.getVal3() );
// // //매수전 현재가보다 3% 낮은 가격으로 매수하기 위한 수치
// // A05StrategryScheduler.BUY_DECRESE_RATE = Double.parseDouble(
// bean.getVal4() );
// // ///매수종료시간
// // A05StrategryScheduler.LAST_BUY_TIME = bean.getVal5();
// }
// }
// }

// if(res > 0) {
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// null);
// } else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), null);
// }

// }

// //맴버 전략스위치
// @PostMapping(value = "/turnStrategyStockSwitchOnOff")
// public Map<String, Object>
// turnStrategyStockSwitchOnOff(@RequestParam(value="memberId", required=true)
// String memberId,
// @RequestParam(value="strategyId", required=true) String strategyId,
// @RequestParam(value="stockNo", required=true) String stockNo,
// @RequestParam(value="stockName", required=true) String stockName,
// @RequestParam(value="buySwitchBtn", required=false) String buySwitchBtn,
// @RequestParam(value="sellSwitchBtn", required=false) String sellSwitchBtn,
// @RequestParam(value="val1", required=false) String val1,
// @RequestParam(value="val2", required=false) String val2,
// @RequestParam(value="val3", required=false) String val3,
// @RequestParam(value="val4", required=false) String val4,
// @RequestParam(value="val5", required=false) String val5,
// HttpServletRequest request,
// HttpServletResponse response) throws Exception {
// int res = memberService.turnStrategyStockSwitchOnOff(strategyId, memberId,
// stockNo, stockName, buySwitchBtn, sellSwitchBtn, val1, val2, val3, val4,
// val5);

// //TODO 해당 전략이 ON/OFF 될때 전략의 static 변수를 교체해준다.
// if( StringUtils.equals(MEMBER_ID, memberId) && "A04".equals(strategyId) &&
// buySwitchBtn != null ) {
// a04Launcher.reloadPdListFromDB();
// }
// else if( StringUtils.equals(MEMBER_ID, memberId) && "A04".equals(strategyId)
// && sellSwitchBtn != null ) {
// a04Launcher.reloadPdListFromDB();
// }

// if(res > 0) {
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// null);
// } else {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(), null);
// }
// }

// @GetMapping(value="/getMemberStrategyStockSwitchList")
// public Map<String, Object>
// getMemberStrategyStockSwitchList(@RequestParam(value="memberId",
// required=true) String memberId,
// @RequestParam(value="strategyId", required=true) String strategyId,
// HttpServletRequest request,
// HttpServletResponse response) throws Exception {
// return ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// memberService.selectMemberStrategyStockSwitchList(strategyId, memberId));
// }

// @PostMapping(value="/deleteMemberStrategyStockList")
// public Map<String, Object> deleteMemberStrategyStockList(@RequestBody
// List<Long> stockPkList,
// HttpServletRequest request,
// HttpServletResponse response) throws Exception {
// if(stockPkList == null && stockPkList.size() == 0) {
// return ResUtils.getMakeDefaultFailResultMsg(request.getRequestURI(),
// CommonException.INVALID_PARAM.getMessage());
// }

// Map<String, Object> rtnMap =
// ResUtils.getMakeDefaultSuccessResultMsg(request.getRequestURI(),
// memberService.deleteMemberStrategyStockList(stockPkList));

// //ON/OFF 시마다 해당 전략을 갱신해준다.
// a04Launcher.reloadPdListFromDB();

// return rtnMap;

// }

// }
