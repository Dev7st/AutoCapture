"""
스케줄링 모듈.

교시별 캡처 스케줄을 관리하고 자동 실행합니다.
"""

import logging
from datetime import datetime, time
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


# 상수 정의
RETRY_INTERVAL = 10  # 재시도 간격 (초)


class CaptureScheduler:
    """
    캡처 스케줄링 클래스.

    교시별 캡처 시간대를 관리하고, 10초 간격으로 callback을 호출합니다.

    Attributes:
        schedules (List[Dict]): 스케줄 목록
        is_running (bool): 실행 중 여부

    Example:
        >>> scheduler = CaptureScheduler()
        >>> scheduler.add_schedule(1, "09:30", "09:45", capture_callback)
        >>> scheduler.start()
    """

    def __init__(self) -> None:
        """
        CaptureScheduler를 초기화합니다.

        스케줄 목록과 실행 상태를 초기화합니다.
        """
        self.schedules: List[Dict] = []
        self.is_running: bool = False

        logger.info("CaptureScheduler 초기화 완료")
