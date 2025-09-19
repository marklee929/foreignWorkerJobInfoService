package fwj.aniss.api.common.bean;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.Data;

/**
 * 공통 Bean
 * 
 * @author SJG
 */
@Data
public class CommonBean implements Serializable {

	private static final long serialVersionUID = 963667530770512587L;

	/** 토큰 **/
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String authToken;
	/** uuid **/
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String uuid;
	/** 등록날짜 **/
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String regDate;
	/** 수정날짜 **/
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String updDate;
	/** 푸시키 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String pushKey;
	/** SMS 메세지 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String message;
	/** 게시판 유형 코드 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String bdTypeCd;
	/* 검색어 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String isShow;
	/* 관심타입 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String favorateType;
	/* 유저타입 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String userType;
	/* 관리자여부 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String isAdmin;

	/** 페이징용 ***/
	/**
	 * 화면에 표시할 페이지를 계산한다.
	 * 
	 * @param totalRecordCount : 전체 레코드 갯수
	 */
	/** 총 조회 수 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int total;
	/** rowNum */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private long rowNum;
	/** 페이지 번호 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int pageNum;
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String countPerRecordTypeCd;
	/** 한 화면에 보여줄 페이지 수 (변경가능하게 set/get 추가함) */
	private int countPerPage = 10;
	/** 페이지당 보여줄 레코드수 (변경가능하게 set/get 추가함) */
	private int countPerRecord = 10;
	/** 전체 레코드수 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int totalRecordCount;
	/** 전체 페이지 수 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int totalPageCount;
	/** 전체 페이지의 그룹갯수 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int totalGroupCount;
	/** 현재 페이지의 그룹번호 (그룹번호는 1부터 시작) */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int groupNo;
	/** 시작 페이지 번호 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int pageStartNo;
	/** 끝 페이지 번호 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int pageEndNo;
	/** 요청 페이지 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int pageNo;
	/** DB 시작 로우 번호 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int startRow;
	/** DB 종료 로우 번호 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private int endRow;

	public void calcPage(int totalRecordCount) {
		// 페이지 디폴트값은 무조건 1 이다.
		this.pageNo = pageNo == 0 ? 1 : pageNo;
		this.totalRecordCount = totalRecordCount;

		// 전체 페이지 갯수
		totalPageCount = calculateTotalPageCount(totalRecordCount, this.getCountPerRecord());
		// DB에서 가져올 시작행 번호
		// startRow = ((pageNo - 1) * countPerRecord) + 1;
		// mysql limit 를 사용하므로 +1은 사용안한다.
		int startRow = this.getStartRow();
		startRow = (pageNo - 1) * this.getCountPerRecord();

		// DB에서 가져올 끝행 번호
		endRow = pageNo * this.getCountPerRecord();

		// 전체 페이징 그룹 갯수
		totalGroupCount = calculateTotalPageCount(totalPageCount, countPerPage);
		// 현재 페이지의 소속 그룹번호
		groupNo = calculateTotalPageCount(pageNo, countPerPage);
		// 시작, 끝 페이지번호 구하기
		// 게시물총수가 0일때는 스타트번호를 0으로 줌
		if (totalRecordCount == 0) {
			pageStartNo = 1;
		} else {
			pageStartNo = ((groupNo - 1) * countPerPage) + 1;
		}
		pageEndNo = groupNo * countPerPage;

		// 마지막 페이지 번호보다 같거나 크다면 더이상의 페이지가 없는것이기 때문에 전체 페이지 갯수를 대입해준다.
		if (pageEndNo >= totalPageCount) {
			pageEndNo = totalPageCount == 0 ? 1 : totalPageCount;
		}
	}

	/**
	 * 전체 레코드 개수에 대한 화면에 표시할 페이징 계산
	 * 
	 * @param totalCount
	 * @return
	 */
	private int calculateTotalPageCount(int totalRecordCount, int countPerPage) {
		int totalPageCount = 0;
		if (totalRecordCount > 0) {
			totalPageCount = totalRecordCount / countPerPage;
			if ((totalRecordCount % countPerPage) > 0) {
				totalPageCount++;
			}
		}
		return totalPageCount;
	}

	/** 페이징 여부 */
	private boolean paging = true;

	/** 검색용 ***/
	/** 검색 시작 날짜 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String startDate;
	/** 검색 종료 날짜 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String endDate;
	/** 검색 시작일 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String strDt;
	/** 검색 종료일 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String endDt;
	/* 카테고리 리스트 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private List<String> categorysList;
	/* 키워드 리스트 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private List<String> keywordsList;
	/* 검색어 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String keyword;

	/** 필터적용 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private List<String> sortList;
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private String sort;
	/** 정렬 맵핑 */
	@JsonInclude(JsonInclude.Include.NON_NULL)
	private Map<String, Object> orderBy;
}