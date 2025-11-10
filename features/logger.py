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
