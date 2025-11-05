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

    def add_schedule(
        self,
        period: int,
        start_time: str,
        end_time: str,
        callback: Callable
    ) -> None:
        """
        스케줄을 추가합니다.

        Args:
            period: 교시 번호 (1~8: 교시, 0: 퇴실)
            start_time: 시작 시간 (HH:MM 형식, 예: "09:30")
            end_time: 종료 시간 (HH:MM 형식, 예: "09:45")
            callback: 캡처 시도 시 호출할 함수

        Raises:
            ValueError: 잘못된 시간 형식이거나 start_time >= end_time인 경우

        Example:
            >>> scheduler.add_schedule(1, "09:30", "09:45", capture_func)
        """
        try:
            # 시간 형식 검증
            start_hour, start_min = map(int, start_time.split(":"))
            end_hour, end_min = map(int, end_time.split(":"))

            # 시간 범위 검증
            if not (0 <= start_hour < 24 and 0 <= start_min < 60):
                raise ValueError(
                    f"잘못된 시작 시간: {start_time}"
                )
            if not (0 <= end_hour < 24 and 0 <= end_min < 60):
                raise ValueError(
                    f"잘못된 종료 시간: {end_time}"
                )

            # 시작 시간 < 종료 시간 검증
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            if start_minutes >= end_minutes:
                raise ValueError(
                    f"시작 시간이 종료 시간보다 늦습니다: "
                    f"{start_time} >= {end_time}"
                )

            # 스케줄 추가
            schedule = {
                "period": period,
                "start_time": start_time,
                "end_time": end_time,
                "callback": callback,
                "is_skipped": False,
                "is_completed": False,
            }
            self.schedules.append(schedule)

            logger.info(
                f"스케줄 추가 완료: 교시={period}, "
                f"시간={start_time}~{end_time}"
            )

        except ValueError as e:
            logger.error(f"스케줄 추가 실패: {e}")
            raise
