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
