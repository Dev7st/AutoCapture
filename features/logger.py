"""
CSV 로그 기록 모듈.

이 모듈은 캡처 이벤트를 CSV 파일로 기록합니다.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional


class CSVLogger:
    """
    CSV 로그 기록 클래스.

    캡처 프로세스의 모든 이벤트를 CSV 파일로 기록합니다.
    UTF-8-BOM 인코딩을 사용하여 Excel 호환성을 보장합니다.

    Attributes:
        base_path (Path): 기본 저장 경로
        log_path (Path): 로그 파일 경로

    Example:
        >>> logger = CSVLogger("C:/IBM 비대면")
        >>> logger._ensure_log_file()  # 로그 파일 생성 (날짜별 폴더 자동 생성)
        >>> logger.log_event("1교시", "캡처 성공", 20, 22, "251020_1교시.png")
    """

    def __init__(self, base_path: str = "C:/IBM 비대면"):
        """
        CSVLogger 초기화.

        Args:
            base_path: 기본 저장 경로
        """
        self.base_path = Path(base_path)
        self.log_path: Optional[Path] = None

    def _ensure_log_file(self) -> None:
        """
        로그 파일이 없으면 헤더와 함께 생성합니다.

        UTF-8-BOM 인코딩을 사용하여 Excel에서 한글이 깨지지 않도록 합니다.
        파일이 이미 존재하면 아무 작업도 하지 않습니다.

        CSV 헤더:
            날짜, 시간, 항목, 상태, 감지인원, 기준인원, 파일명, 비고

        Raises:
            OSError: 파일 생성 실패 시
        """
        if self.log_path is None:
            # 로그 경로가 설정되지 않았으면 현재 날짜로 설정
            today = datetime.now().strftime("%y%m%d")
            date_folder = self.base_path / today
            date_folder.mkdir(parents=True, exist_ok=True)
            self.log_path = date_folder / f"{today}_log.csv"

        # 파일이 이미 존재하면 아무 작업도 안 함
        if self.log_path.exists():
            return

        # 파일이 없으면 헤더와 함께 생성
        try:
            with open(self.log_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    '날짜', '시간', '항목', '상태',
                    '감지인원', '기준인원', '파일명', '비고'
                ])
        except OSError as e:
            raise OSError(f"로그 파일 생성 실패: {self.log_path}") from e
