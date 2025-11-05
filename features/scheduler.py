"""
스케줄링 모듈.

교시별 캡처 스케줄을 관리하고 자동 실행합니다.
"""

import logging
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# 상수 정의
RETRY_INTERVAL = 10  # 재시도 간격 (초)
CHECK_INTERVAL = 1000  # 스케줄 체크 간격 (밀리초)


class CaptureScheduler:
    """
    캡처 스케줄링 클래스.

    교시별 캡처 시간대를 관리하고, 10초 간격으로 callback을 호출합니다.

    Attributes:
        schedules (List[Dict]): 스케줄 목록
        is_running (bool): 실행 중 여부
        _root (Optional[Any]): tkinter 루트 윈도우
        _last_attempt (Dict[int, int]): 교시별 마지막 시도 시간 (초)

    Example:
        >>> scheduler = CaptureScheduler()
        >>> scheduler.add_schedule(1, "09:30", "09:45", capture_callback)
        >>> scheduler.start(root)
    """

    def __init__(self) -> None:
        """
        CaptureScheduler를 초기화합니다.

        스케줄 목록과 실행 상태를 초기화합니다.
        """
        self.schedules: List[Dict] = []
        self.is_running: bool = False
        self._root: Optional[Any] = None
        self._last_attempt: Dict[int, int] = {}

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

    def is_in_capture_window(self, period: int) -> bool:
        """
        현재 시간이 캡처 시간대인지 확인합니다.

        Args:
            period: 교시 번호 (1~8: 교시, 0: 퇴실)

        Returns:
            bool: 캡처 시간대 여부 (True: 시간대 내, False: 시간대 외)

        Example:
            >>> scheduler.is_in_capture_window(1)
            True  # 현재 시간이 09:30~09:45 사이인 경우
        """
        # 해당 교시의 스케줄 찾기
        schedule = None
        for s in self.schedules:
            if s["period"] == period:
                schedule = s
                break

        if schedule is None:
            logger.warning(f"교시 {period}의 스케줄을 찾을 수 없습니다")
            return False

        # 현재 시간 가져오기
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # 시간대 확인
        start_time = schedule["start_time"]
        end_time = schedule["end_time"]

        # 시간 문자열을 분으로 변환하여 비교
        def time_to_minutes(time_str: str) -> int:
            """HH:MM 형식을 분 단위로 변환"""
            hour, minute = map(int, time_str.split(":"))
            return hour * 60 + minute

        current_minutes = time_to_minutes(current_time)
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)

        return start_minutes <= current_minutes < end_minutes

    def start(self, root: Any) -> None:
        """
        스케줄러를 시작합니다.

        tkinter의 after() 메서드를 사용하여 1초마다 스케줄을 체크합니다.

        Args:
            root: tkinter 루트 윈도우 (tk.Tk 또는 tk.Toplevel)

        Raises:
            RuntimeError: 이미 실행 중인 경우

        Example:
            >>> scheduler.start(root)
        """
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            raise RuntimeError("스케줄러가 이미 실행 중입니다")

        self._root = root
        self.is_running = True
        logger.info("스케줄러 시작")

        # 첫 체크 시작
        self._check_schedules()

    def _check_schedules(self) -> None:
        """
        모든 스케줄을 체크하고 필요 시 callback을 호출합니다.

        1초마다 호출되며, 10초 간격으로 callback을 실행합니다.
        """
        if not self.is_running:
            return

        try:
            current_timestamp = int(datetime.now().timestamp())

            for schedule in self.schedules:
                period = schedule["period"]

                # 건너뛰기 또는 완료된 교시는 무시
                if schedule["is_skipped"] or schedule["is_completed"]:
                    continue

                # 캡처 시간대인지 확인
                if not self.is_in_capture_window(period):
                    continue

                # 마지막 시도 시간 확인 (10초 간격)
                last_attempt = self._last_attempt.get(period, 0)
                if current_timestamp - last_attempt < RETRY_INTERVAL:
                    continue

                # callback 호출
                self._last_attempt[period] = current_timestamp
                callback = schedule["callback"]
                callback(period)

        except Exception as e:
            logger.error(f"스케줄 체크 중 오류: {e}", exc_info=True)

        # 1초 후 다시 체크
        if self._root is not None:
            self._root.after(CHECK_INTERVAL, self._check_schedules)

    def stop(self) -> None:
        """
        스케줄러를 중지합니다.

        is_running 플래그를 False로 설정하여
        _check_schedules()의 재귀 호출을 중단합니다.

        Example:
            >>> scheduler.stop()
        """
        if not self.is_running:
            logger.warning("스케줄러가 실행 중이 아닙니다")
            return

        self.is_running = False
        logger.info("스케줄러 중지")
