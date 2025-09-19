package fwj.aniss.api.common.service.board;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import fwj.aniss.api.common.bean.board.BoardBean;
import fwj.aniss.api.common.daos.BoardDao;

@Service
public class BoardService {

	@Autowired
	private BoardDao boardDao;

	public int insertBoard(BoardBean bean) {
		return boardDao.insertBoard(bean);
	}

	public int updateBoard(BoardBean bean) {
		return boardDao.updateBoard(bean);
	}

	public int deleteBoard(BoardBean bean) {
		return boardDao.deleteBoard(bean);
	}

	public BoardBean selectBoard(BoardBean bean) {
		return boardDao.selectBoard(bean);
	}

	// 전체 글의 갯수조회
	public int selectBoardListCount(BoardBean bean) {
		return boardDao.selectBoardListCount(bean);
	}

	public List<BoardBean> selecetBoardList(BoardBean bean) {
		return boardDao.selectBoardList(bean);
	}

}