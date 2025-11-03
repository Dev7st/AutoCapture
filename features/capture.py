"""
화면 캡처 모듈.

선택된 모니터의 화면을 캡처하는 기능을 제공합니다.
듀얼 모니터 환경을 지원하며, mss 라이브러리를 사용합니다.
"""

# 표준 라이브러리
import logging

# 외부 라이브러리
import mss
import numpy as np
from typing import Optional

# 로거 설정
logger = logging.getLogger(__name__)


class ScreenCapture:
    """
    화면 캡처 클래스.

    선택된 모니터의 전체 화면을 캡처하여
    RGB 형식의 numpy array로 반환합니다.

    Attributes:
        monitor_id: 캡처할 모니터 ID (1부터 시작)
        _sct: mss 인스턴스 (화면 캡처용)

    Example:
        >>> capturer = ScreenCapture(monitor_id=1)
        >>> image = capturer.capture()
        >>> print(image.shape)  # (height, width, 3)
        (1080, 1920, 3)
    """

    def __init__(self, monitor_id: int = 1) -> None:
        """
        ScreenCapture 인스턴스를 초기화합니다.

        Args:
            monitor_id: 캡처할 모니터 ID (기본값: 1)
                       1부터 시작하며, 연결된 모니터 개수를 초과할 수 없습니다.

        Raises:
            ValueError: monitor_id가 1보다 작은 경우
            RuntimeError: mss 인스턴스 생성 실패 시

        Example:
            >>> capturer = ScreenCapture(monitor_id=2)
            >>> capturer.monitor_id
            2
        """
        if monitor_id < 1:
            raise ValueError(f"monitor_id는 1 이상이어야 합니다. 입력값: {monitor_id}")

        self.monitor_id: int = monitor_id
        self._sct: Optional[mss.mss] = None

        try:
            self._sct = mss.mss()
        except Exception as e:
            logger.error(f"mss 인스턴스 생성 실패: {e}", exc_info=True)
            raise RuntimeError(f"mss 인스턴스 생성 실패: {e}")
