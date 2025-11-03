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

    def capture(self) -> np.ndarray:
        """
        선택된 모니터의 화면을 캡처합니다.

        mss 라이브러리를 사용하여 전체 화면(작업표시줄 포함)을 캡처하고,
        BGR 형식을 RGB 형식으로 변환하여 반환합니다.

        Returns:
            np.ndarray: RGB 형식의 캡처 이미지 (height, width, 3)

        Raises:
            RuntimeError: 화면 캡처 실패 시
            IndexError: 유효하지 않은 모니터 ID인 경우

        Example:
            >>> capturer = ScreenCapture(monitor_id=1)
            >>> image = capturer.capture()
            >>> print(image.shape)
            (1080, 1920, 3)
            >>> print(image.dtype)
            uint8
        """
        try:
            # mss.monitors[0]은 전체 화면, [1:]부터 실제 모니터
            monitor = self._sct.monitors[self.monitor_id]

            # 화면 캡처
            screenshot = self._sct.grab(monitor)

            # numpy array로 변환 (BGRA 형식)
            image = np.array(screenshot)

            # BGRA -> RGB 변환 (Alpha 채널 제거)
            image_rgb = image[:, :, :3]  # BGR 채널만 추출
            image_rgb = image_rgb[:, :, ::-1]  # BGR -> RGB 변환

            return image_rgb

        except IndexError as e:
            logger.error(f"유효하지 않은 모니터 ID: {self.monitor_id}", exc_info=True)
            raise IndexError(
                f"모니터 ID {self.monitor_id}를 찾을 수 없습니다. "
                f"연결된 모니터 개수를 확인하세요."
            )
        except Exception as e:
            logger.error(f"화면 캡처 실패: {e}", exc_info=True)
            raise RuntimeError(f"화면 캡처 실패: {e}")
