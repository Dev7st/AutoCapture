"""
파일 저장 관리 모듈.

캡처된 이미지를 날짜별 폴더에 저장하고 파일명 규칙을 관리합니다.
"""

# 표준 라이브러리
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# 외부 라이브러리
import numpy as np
from PIL import Image

# 로거 설정
logger = logging.getLogger(__name__)


class FileManager:
    """
    파일 저장 관리 클래스.

    캡처된 이미지를 날짜별 폴더에 저장하고, 교시별 파일명 규칙을 적용합니다.
    중복 파일 처리(덮어쓰기/수정본) 로직을 포함합니다.

    Attributes:
        base_path: 기본 저장 경로 (Path 객체)
        current_date: 현재 날짜 문자열 (YYMMDD 형식)

    Example:
        >>> fm = FileManager("C:/IBM 비대면")
        >>> file_path = fm.save_image(image, period=1, is_modified=False)
        "C:/IBM 비대면/251104/251104_1교시.png"
    """

    def __init__(self, base_path: str = "C:/IBM 비대면") -> None:
        """
        FileManager 인스턴스를 초기화합니다.

        기본 저장 경로를 설정하고 현재 날짜를 YYMMDD 형식으로 계산합니다.

        Args:
            base_path: 기본 저장 경로 (기본값: "C:/IBM 비대면")

        Example:
            >>> fm = FileManager()  # 기본 경로 사용
            >>> fm = FileManager("D:/출결관리")  # 사용자 지정 경로
        """
        self.base_path: Path = Path(base_path)
        self.current_date: str = datetime.now().strftime("%y%m%d")

        logger.info(f"FileManager 초기화: base_path={self.base_path}, date={self.current_date}")

    def ensure_folder_exists(self) -> None:
        """
        날짜별 폴더를 생성합니다.

        base_path 아래에 current_date 폴더를 생성합니다.
        폴더가 이미 존재하면 아무 작업도 하지 않습니다.

        Raises:
            PermissionError: 폴더 생성 권한이 없을 때
            OSError: 폴더 생성 중 오류 발생 시

        Example:
            >>> fm = FileManager("C:/IBM 비대면")
            >>> fm.ensure_folder_exists()
            # C:/IBM 비대면/251104/ 폴더 생성
        """
        try:
            folder_path = self.base_path / self.current_date
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"폴더 확인/생성 완료: {folder_path}")

        except PermissionError as e:
            logger.error(f"폴더 생성 권한 없음: {folder_path}", exc_info=True)
            raise PermissionError(f"폴더를 생성할 권한이 없습니다: {folder_path}")

        except Exception as e:
            logger.error(f"폴더 생성 실패: {e}", exc_info=True)
            raise OSError(f"폴더 생성 중 오류 발생: {e}")

    def get_file_path(self, period: int, is_modified: bool = False) -> Path:
        """
        파일 경로를 생성합니다.

        교시 번호와 수정본 여부에 따라 파일 경로를 생성합니다.

        Args:
            period: 교시 번호 (0=퇴실, 1~8=교시)
            is_modified: 수정본 여부
                        False: 일반 파일 (덮어쓰기)
                        True: 수정본 파일 (_수정.png)

        Returns:
            Path: 생성된 파일 경로

        Raises:
            ValueError: period가 0~8 범위를 벗어날 때

        Example:
            >>> fm = FileManager("C:/IBM 비대면")
            >>> path = fm.get_file_path(1, False)
            Path("C:/IBM 비대면/251104/251104_1교시.png")

            >>> path = fm.get_file_path(1, True)
            Path("C:/IBM 비대면/251104/251104_1교시_수정.png")

            >>> path = fm.get_file_path(0, False)
            Path("C:/IBM 비대면/251104/251104_퇴실.png")
        """
        # period 유효성 검사
        if not isinstance(period, int):
            logger.error(f"period는 정수여야 합니다. 현재: {type(period)}")
            raise ValueError(f"period는 정수여야 합니다. 현재: {type(period)}")

        if period < 0 or period > 8:
            logger.error(f"period는 0~8 범위여야 합니다. 현재: {period}")
            raise ValueError(f"period는 0~8 범위여야 합니다. 현재: {period}")

        # 교시명 가져오기
        period_name = self._get_period_name(period)

        # 파일명 생성
        if is_modified:
            filename = f"{self.current_date}_{period_name}_수정.png"
        else:
            filename = f"{self.current_date}_{period_name}.png"

        # 전체 경로 생성
        file_path = self.base_path / self.current_date / filename

        logger.info(f"파일 경로 생성: {file_path}")
        return file_path

    def _get_period_name(self, period: int) -> str:
        """
        교시 번호를 교시명으로 변환합니다.

        Args:
            period: 교시 번호 (0=퇴실, 1~8=교시)

        Returns:
            str: 교시명 ("퇴실" 또는 "N교시")

        Example:
            >>> fm = FileManager()
            >>> fm._get_period_name(0)
            "퇴실"
            >>> fm._get_period_name(1)
            "1교시"
            >>> fm._get_period_name(8)
            "8교시"
        """
        if period == 0:
            return "퇴실"
        else:
            return f"{period}교시"
