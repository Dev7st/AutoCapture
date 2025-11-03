"""
메인 윈도우 모듈.

출결 관리 자동 캡처 프로그램의 메인 GUI를 제공합니다.
"""

# 표준 라이브러리
import logging
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Optional, Dict

# 로거 설정
logger = logging.getLogger(__name__)


class MainWindow:
    """
    메인 윈도우 클래스.

    프로그램의 메인 GUI를 제공하며, 다음 기능을 포함합니다:
    - 실시간 날짜/시간 표시
    - 캡처 모드 및 인원 관리
    - 교시별 캡처 상태 표시 (1~8교시 + 퇴실)
      * 🕒 대기중
      * 🔍 감지중 (N명)
      * ✅ 완료
      * ⏭️ 건너뛰기
      * ⏰ 시간 초과
    - 건너뛰기/재시도 기능
    - 저장 경로 관리

    Attributes:
        root (tk.Tk): tkinter 루트 윈도우
        config (Dict): 초기 설정값
        monitor_id (int): 선택된 모니터 ID
        save_path (str): 저장 경로
        mode (str): 캡처 모드 ('exact' or 'flexible')
        student_count (int): 출석 학생 수

    Example:
        >>> window = MainWindow(config)
        >>> window.run()
    """

    # ==================== Initialization ====================

    def __init__(self, config: Dict):
        """
        메인 윈도우를 초기화합니다.

        Args:
            config: InitDialog에서 반환된 설정값
                   {'monitor_id': int, 'save_path': str,
                    'mode': str, 'student_count': int}
        """
        self.root = tk.Tk()
        self.root.title("출결 관리 자동 캡처 시스템")
        self.root.geometry("750x820")
        self.root.resizable(False, False)

        # 설정값 저장
        self.config = config
        self.monitor_id: int = config.get('monitor_id', 1)
        self.save_path: str = config.get('save_path', 'C:/IBM 비대면')
        self.mode: str = config.get('mode', 'flexible')
        self.student_count: int = config.get('student_count', 1)

        # UI 변수
        self.date_var: Optional[tk.StringVar] = None
        self.time_var: Optional[tk.StringVar] = None
        self.status_var: Optional[tk.StringVar] = None
        self.monitor_var: Optional[tk.StringVar] = None
        self.mode_var: Optional[tk.StringVar] = None
        self.student_count_var: Optional[tk.IntVar] = None
        self.threshold_label: Optional[ttk.Label] = None

        # 교시별 상태 변수 (1~8교시 + 퇴실)
        self.period_status_vars: Dict[int, tk.StringVar] = {}

        # 교시별 캡처 시간대 정보 초기화
        self.period_end_times: Dict[int, tuple] = self._initialize_period_times()

        # UI 구성
        self.setup_ui()

        # 시간 업데이트 시작
        self.update_time()

    def _initialize_period_times(self) -> Dict[int, tuple]:
        """
        교시별 캡처 종료 시간 정보를 반환합니다.

        Returns:
            Dict[int, tuple]: {교시번호: (종료_시, 종료_분)}
        """
        return {
            1: (9, 45),   # 1교시: 09:30~09:45
            2: (10, 45),  # 2교시: 10:30~10:45
            3: (11, 45),  # 3교시: 11:30~11:45
            4: (12, 45),  # 4교시: 12:30~12:45
            5: (14, 45),  # 5교시: 14:30~14:45
            6: (15, 45),  # 6교시: 15:30~15:45
            7: (16, 45),  # 7교시: 16:30~16:45
            8: (17, 45),  # 8교시: 17:30~17:45
            0: (18, 32),  # 퇴실: 18:30~18:32
        }

    def setup_ui(self) -> None:
        """
        UI 구성요소를 배치합니다.

        메인 윈도우를 5개 섹션으로 구성:
        1. 상단 정보 영역 (날짜/시간/상태/모니터)
        2. 인원 관리 영역 (모드/학생수/기준인원)
        3. 교시별 상태 영역 (1~8교시 + 퇴실)
        4. 하단 버튼 영역 (저장 경로/폴더 열기)
        """
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="30 30 30 30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 상단 정보 영역
        self._create_info_section(main_frame)

        # 2. 인원 관리 영역
        self._create_personnel_section(main_frame)

        # 3. 교시별 상태 영역
        self._create_period_section(main_frame)

        # 4. 하단 버튼 영역
        self._create_bottom_buttons(main_frame)

    def run(self) -> None:
        """
        메인 윈도우를 실행합니다.

        이벤트 루프를 시작하고 윈도우가 닫힐 때까지 대기합니다.
        """
        logger.info("메인 윈도우 실행 시작")
        self.root.mainloop()
        logger.info("메인 윈도우 종료")

    # ==================== Info Section ====================

    def _create_info_section(self, parent: ttk.Frame) -> None:
        """
        상단 정보 영역을 생성합니다.

        날짜, 시간, 현재 상태, 캡처 모니터를 표시합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="현재 정보",
            padding="15 15 15 15"
        )
        section_frame.pack(fill=tk.X, pady=(0, 15))

        # 날짜 표시
        self.date_var = tk.StringVar(value="날짜: 로딩 중...")
        date_label = ttk.Label(
            section_frame,
            textvariable=self.date_var,
            font=("", 14)
        )
        date_label.pack(anchor=tk.W, pady=(0, 10))

        # 시간 표시
        self.time_var = tk.StringVar(value="시간: 로딩 중...")
        time_label = ttk.Label(
            section_frame,
            textvariable=self.time_var,
            font=("", 14)
        )
        time_label.pack(anchor=tk.W, pady=(0, 10))

        # 현재 상태 표시
        self.status_var = tk.StringVar(value="현재: 프로그램 시작")
        status_label = ttk.Label(
            section_frame,
            textvariable=self.status_var,
            font=("", 14)
        )
        status_label.pack(anchor=tk.W, pady=(0, 10))

        # 캡처 모니터 표시
        self._create_monitor_display(section_frame)

    def _create_monitor_display(self, parent: ttk.LabelFrame) -> None:
        """
        캡처 모니터 표시 및 변경 버튼을 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 모니터 표시 영역
        monitor_frame = ttk.Frame(parent)
        monitor_frame.pack(fill=tk.X)

        # 모니터 정보 표시
        self.monitor_var = tk.StringVar(
            value=f"캡처 모니터: 모니터 {self.monitor_id}"
        )
        monitor_label = ttk.Label(
            monitor_frame,
            textvariable=self.monitor_var,
            font=("", 14)
        )
        monitor_label.pack(side=tk.LEFT)

        # [변경] 버튼
        change_button = ttk.Button(
            monitor_frame,
            text="변경",
            width=8,
            command=self._on_change_monitor
        )
        change_button.pack(side=tk.LEFT, padx=(10, 0))

    def update_time(self) -> None:
        """
        현재 날짜와 시간을 업데이트합니다.

        1초마다 자동으로 호출되어 실시간으로 갱신됩니다.
        캡처 시간대가 지난 교시는 자동으로 "⏰ 시간 초과"로 변경합니다.
        """
        try:
            now = datetime.now()
            self.date_var.set(f"📅 날짜: {now.strftime('%Y-%m-%d')}")
            self.time_var.set(f"⏰ 시간: {now.strftime('%H:%M:%S')}")

            # TODO: 다음 교시까지 남은 시간 계산 (Phase 2에서 구현)
            self.status_var.set("📚 현재: 대기 중")

            # 시간 초과된 교시 체크
            self._check_timeout_periods(now)

        except Exception as e:
            logger.error(f"시간 업데이트 실패: {e}")

        # 1초 후 재호출
        self.root.after(1000, self.update_time)

    def _on_change_monitor(self) -> None:
        """
        모니터 변경 버튼 클릭 핸들러.

        TODO: Phase 3에서 모니터 선택 다이얼로그 구현
        """
        try:
            logger.info("모니터 변경 버튼 클릭")
            messagebox.showinfo(
                "개발 중",
                "모니터 변경 기능은 Phase 3에서 구현 예정입니다."
            )
            # TODO: 모니터 선택 다이얼로그 표시 후
            # self.monitor_id = selected_monitor_id
            # self.monitor_var.set(f"캡처 모니터: 모니터 {self.monitor_id}")
            # logger.info(f"모니터 변경: 모니터 {self.monitor_id}")
        except Exception as e:
            logger.error(f"모니터 변경 처리 실패: {e}")
            messagebox.showerror("오류", f"모니터 변경 중 오류가 발생했습니다.\n{e}")

    def _check_timeout_periods(self, now: datetime) -> None:
        """
        캡처 시간대가 지난 교시를 확인하고 "⏰ 시간 초과"로 변경합니다.

        Args:
            now: 현재 시간
        """
        try:
            current_hour = now.hour
            current_minute = now.minute

            for period, (end_hour, end_minute) in self.period_end_times.items():
                # 현재 상태 확인
                current_status = self.period_status_vars.get(period)
                if not current_status:
                    continue

                status_text = current_status.get()

                # 이미 완료, 건너뛰기, 시간 초과 상태면 변경하지 않음
                if "✅" in status_text or "⏭️" in status_text or "⏰" in status_text:
                    continue

                # 현재 시간이 캡처 종료 시간을 지났는지 확인
                if (current_hour > end_hour or
                    (current_hour == end_hour and current_minute > end_minute)):
                    # 대기중 상태만 시간 초과로 변경 (감지중은 그대로 유지)
                    if "🕒" in status_text:
                        self.update_period_status(period, "⏰ 시간 초과")
        except Exception as e:
            logger.error(f"시간 초과 교시 체크 실패: {e}")

    # ==================== Personnel Section ====================

    def _create_personnel_section(self, parent: ttk.Frame) -> None:
        """
        인원 관리 영역을 생성합니다.

        캡처 모드, 출석 학생 수, 기준 인원을 관리합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="👥 출석 관리",
            padding="15 15 15 15"
        )
        section_frame.pack(fill=tk.X, pady=(0, 15))

        # 캡처 모드 선택
        self._create_mode_selector(section_frame)

        # 구분선
        ttk.Separator(section_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=15
        )

        # 출석 학생 수 입력
        self._create_student_count_input(section_frame)

        # 기준 인원 표시
        self._create_threshold_display(section_frame)

    def _create_mode_selector(self, parent: ttk.LabelFrame) -> None:
        """
        캡처 모드 선택 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 모드 선택 영역
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, pady=(0, 0))

        # 레이블
        mode_label = ttk.Label(
            mode_frame,
            text="캡처 모드:",
            font=("", 12)
        )
        mode_label.pack(side=tk.LEFT, padx=(0, 10))

        # 모드 변수 초기화
        self.mode_var = tk.StringVar(value=self.mode)

        # 콤보박스
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            values=["유연 모드 (권장)", "정확 모드"],
            state="readonly",
            width=20,
            font=("", 11)
        )
        mode_combo.pack(side=tk.LEFT)

        # 기본값 설정
        if self.mode == "flexible":
            mode_combo.current(0)  # 유연 모드
        else:
            mode_combo.current(1)  # 정확 모드

        # 모드 변경 시 로깅
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

    def _create_student_count_input(self, parent: ttk.LabelFrame) -> None:
        """
        출석 학생 수 입력 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 입력 영역
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # 레이블
        label = ttk.Label(
            input_frame,
            text="출석 학생 수:",
            font=("", 12)
        )
        label.pack(side=tk.LEFT, padx=(0, 10))

        # 학생 수 변수 초기화
        self.student_count_var = tk.IntVar(value=self.student_count)

        # 입력 필드
        count_entry = ttk.Entry(
            input_frame,
            textvariable=self.student_count_var,
            width=8,
            justify=tk.CENTER,
            font=("", 12)
        )
        count_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 직접 입력 시 로깅
        count_entry.bind("<Return>", self._on_student_count_entered)
        count_entry.bind("<FocusOut>", self._on_student_count_entered)

        # 증감 버튼 생성
        self._create_count_buttons(input_frame)

        # 안내 텍스트
        help_label = ttk.Label(
            input_frame,
            text="명 (1~100)",
            font=("", 11),
            foreground="gray"
        )
        help_label.pack(side=tk.LEFT, padx=(5, 0))

    def _create_count_buttons(self, parent: ttk.Frame) -> None:
        """
        학생 수 증감 버튼을 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # ▲ 버튼
        up_button = ttk.Button(
            parent,
            text="▲",
            width=3,
            command=self._increment_student_count
        )
        up_button.pack(side=tk.LEFT, padx=(0, 5))

        # ▼ 버튼
        down_button = ttk.Button(
            parent,
            text="▼",
            width=3,
            command=self._decrement_student_count
        )
        down_button.pack(side=tk.LEFT)

    def _create_threshold_display(self, parent: ttk.LabelFrame) -> None:
        """
        기준 인원 표시 영역을 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 기준 인원 계산
        threshold = self.student_count + 1

        # 기준 인원 레이블
        self.threshold_label = ttk.Label(
            parent,
            text=f"기준 인원: {threshold}명 (학생 {self.student_count}명 + 강사 1명)",
            font=("", 12),
            foreground="blue"
        )
        self.threshold_label.pack(anchor=tk.W)

        # 학생 수 변경 시 자동 업데이트
        self.student_count_var.trace_add("write", self._update_threshold_label)

    def _on_mode_changed(self, event=None) -> None:
        """
        캡처 모드 변경 시 호출되는 콜백 함수.

        Args:
            event: tkinter 이벤트 객체 (사용하지 않음)
        """
        mode_text = self.mode_var.get()
        # 내부 모드 값으로 변환
        if "유연" in mode_text:
            self.mode = "flexible"
        else:
            self.mode = "exact"
        logger.info(f"캡처 모드 변경: {mode_text} ({self.mode})")

    def _on_student_count_entered(self, event=None) -> None:
        """
        학생 수 직접 입력 후 Enter 또는 포커스 아웃 시 호출되는 콜백 함수.

        Args:
            event: tkinter 이벤트 객체 (사용하지 않음)
        """
        student_count = self.student_count_var.get()
        logger.info(f"학생 수 직접 입력: {student_count}명")

    def _increment_student_count(self) -> None:
        """
        학생 수를 1 증가시킵니다.

        최대값 100을 초과하지 않도록 제한합니다.
        """
        current_value = self.student_count_var.get()
        if current_value < 100:
            self.student_count_var.set(current_value + 1)
            logger.info(f"학생 수 증가: {current_value} → {current_value + 1}")

    def _decrement_student_count(self) -> None:
        """
        학생 수를 1 감소시킵니다.

        최소값 1 미만으로 내려가지 않도록 제한합니다.
        """
        current_value = self.student_count_var.get()
        if current_value > 1:
            self.student_count_var.set(current_value - 1)
            logger.info(f"학생 수 감소: {current_value} → {current_value - 1}")

    def _update_threshold_label(self, *args) -> None:
        """
        학생 수 변경 시 기준 인원 레이블을 업데이트합니다.

        Args:
            *args: trace_add 콜백에서 전달되는 인자 (사용하지 않음)
        """
        try:
            student_count = self.student_count_var.get()

            # 범위 검증 및 수정
            if student_count < 1:
                student_count = 1
                self.student_count_var.set(1)
            elif student_count > 100:
                student_count = 100
                self.student_count_var.set(100)

            threshold = student_count + 1
            self.threshold_label.config(
                text=f"기준 인원: {threshold}명 (학생 {student_count}명 + 강사 1명)"
            )
        except Exception as e:
            logger.error(f"기준 인원 업데이트 실패: {e}")
            # 잘못된 값일 경우 기본값으로 설정
            try:
                self.student_count_var.set(1)
                self.threshold_label.config(
                    text="기준 인원: 2명 (학생 1명 + 강사 1명)"
                )
            except:
                pass

    # ==================== Period Section ====================

    def _create_period_section(self, parent: ttk.Frame) -> None:
        """
        교시별 상태 영역을 생성합니다.

        1~8교시 + 퇴실 (총 9개 항목)의 상태를 표시합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="📊 교시별 캡처 상태",
            padding="15 10 15 10"
        )
        section_frame.pack(fill=tk.X, expand=False, pady=(0, 15))

        # 교시 정보 (교시 번호, 시작 시간, 종료 시간, 캡처 시간대)
        periods = [
            (1, "09:30", "10:20", "09:30~09:45"),
            (2, "10:30", "11:20", "10:30~10:45"),
            (3, "11:30", "12:20", "11:30~11:45"),
            (4, "12:30", "13:20", "12:30~12:45"),
            (5, "14:30", "15:20", "14:30~14:45"),
            (6, "15:30", "16:20", "15:30~15:45"),
            (7, "16:30", "17:20", "16:30~16:45"),
            (8, "17:30", "18:20", "17:30~17:45"),
            (0, "18:30", "-", "18:30~18:32")  # 퇴실 (period=0)
        ]

        # 각 교시별 행 생성
        for period, start, end, capture_window in periods:
            self._create_period_row(
                section_frame, period, start, end, capture_window
            )

    def _create_period_row(
        self,
        parent: ttk.LabelFrame,
        period: int,
        start_time: str,
        end_time: str,
        capture_window: str
    ) -> None:
        """
        개별 교시의 상태 표시 행을 생성합니다.

        Args:
            parent: 부모 프레임
            period: 교시 번호 (0=퇴실, 1~8=교시)
            start_time: 시작 시간
            end_time: 종료 시간
            capture_window: 캡처 시간대
        """
        # 교시 행 프레임
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=(0, 8))

        # 교시 정보 및 캡처 시간대 표시
        self._create_period_info_labels(row_frame, period, start_time, end_time, capture_window)

        # 상태 표시 레이블
        self._create_period_status_label(row_frame, period)

        # 건너뛰기/재시도 버튼
        self._create_period_buttons(row_frame, period)

    def _create_period_info_labels(
        self,
        parent: ttk.Frame,
        period: int,
        start_time: str,
        end_time: str,
        capture_window: str
    ) -> None:
        """
        교시 정보 및 캡처 시간대 레이블을 생성합니다.

        Args:
            parent: 부모 프레임
            period: 교시 번호
            start_time: 시작 시간
            end_time: 종료 시간
            capture_window: 캡처 시간대
        """
        # 교시 이름
        period_name = "퇴실" if period == 0 else f"{period}교시"

        # 교시 정보 레이블
        info_text = f"{period_name} ({start_time}~{end_time})"
        info_label = ttk.Label(
            parent,
            text=info_text,
            font=("", 11, "bold"),
            width=25
        )
        info_label.pack(side=tk.LEFT, padx=(0, 10))

        # 캡처 시간대 레이블
        window_label = ttk.Label(
            parent,
            text=f"[{capture_window}]",
            font=("", 10),
            foreground="gray",
            width=18
        )
        window_label.pack(side=tk.LEFT, padx=(0, 15))

    def _create_period_status_label(self, parent: ttk.Frame, period: int) -> None:
        """
        교시 상태 표시 레이블을 생성합니다.

        Args:
            parent: 부모 프레임
            period: 교시 번호
        """
        # 상태 표시 레이블
        status_var = tk.StringVar(value="🕒 대기중")
        self.period_status_vars[period] = status_var
        status_label = ttk.Label(
            parent,
            textvariable=status_var,
            font=("", 10),
            width=15
        )
        status_label.pack(side=tk.LEFT, padx=(0, 10))

    def _create_period_buttons(self, parent: ttk.Frame, period: int) -> None:
        """
        교시별 건너뛰기/재시도 버튼을 생성합니다.

        Args:
            parent: 부모 프레임
            period: 교시 번호
        """
        # [건너뛰기] 버튼
        skip_button = ttk.Button(
            parent,
            text="건너뛰기",
            width=10,
            command=lambda p=period: self.on_skip_button(p)
        )
        skip_button.pack(side=tk.LEFT, padx=(0, 5))

        # [재시도] 버튼
        retry_button = ttk.Button(
            parent,
            text="재시도",
            width=10,
            command=lambda p=period: self.on_retry_button(p)
        )
        retry_button.pack(side=tk.LEFT)

    def update_period_status(self, period: int, status: str) -> None:
        """
        교시 상태를 업데이트합니다.

        Args:
            period: 교시 번호 (0=퇴실, 1~8=교시)
            status: 상태 문자열
                   - "🕒 대기중"
                   - "🔍 감지중 (N명)"
                   - "✅ 완료"
                   - "⏭️ 건너뛰기"
                   - "⏰ 시간 초과"

        Example:
            >>> window.update_period_status(1, "✅ 완료")
            >>> window.update_period_status(2, "🔍 감지중 (20명)")
            >>> window.update_period_status(3, "⏰ 시간 초과")
        """
        try:
            if period in self.period_status_vars:
                self.period_status_vars[period].set(status)
                period_name = "퇴실" if period == 0 else f"{period}교시"
                logger.info(f"{period_name} 상태 변경: {status}")
            else:
                logger.warning(f"존재하지 않는 교시 번호: {period}")
        except Exception as e:
            logger.error(f"교시 상태 업데이트 실패 (교시 {period}): {e}")

    def on_skip_button(self, period: int) -> None:
        """
        건너뛰기 버튼 클릭 핸들러.

        TODO: Phase 2에서 Scheduler와 연동하여 실제 건너뛰기 구현

        Args:
            period: 교시 번호
        """
        period_name = "퇴실" if period == 0 else f"{period}교시"
        logger.info(f"건너뛰기 버튼 클릭: {period_name}")

        # TODO: Scheduler.skip_period(period) 호출
        self.update_period_status(period, "⏭️ 건너뛰기")

    def on_retry_button(self, period: int) -> None:
        """
        재시도 버튼 클릭 핸들러.

        TODO: Phase 2에서 캡처 로직과 연동하여 재시도 구현

        Args:
            period: 교시 번호
        """
        period_name = "퇴실" if period == 0 else f"{period}교시"
        logger.info(f"재시도 버튼 클릭: {period_name}")

        # TODO: 캡처 시간대 확인 후 즉시 캡처 시도
        self.update_period_status(period, "🔍 감지중")

    # ==================== Bottom Buttons ====================

    def _create_bottom_buttons(self, parent: ttk.Frame) -> None:
        """
        하단 버튼 영역을 생성합니다.

        저장 경로 설정 및 폴더 열기 버튼을 제공합니다.

        Args:
            parent: 부모 프레임
        """
        # 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # [저장 경로 설정] 버튼
        path_button = ttk.Button(
            button_frame,
            text="저장 경로 설정",
            width=20,
            command=self._on_set_save_path
        )
        path_button.pack(side=tk.LEFT, padx=(0, 10))

        # [저장 폴더 열기] 버튼
        open_button = ttk.Button(
            button_frame,
            text="저장 폴더 열기",
            width=20,
            command=self._on_open_save_folder
        )
        open_button.pack(side=tk.LEFT)

    def _on_set_save_path(self) -> None:
        """
        저장 경로 설정 버튼 클릭 핸들러.

        폴더 선택 다이얼로그를 표시하고 저장 경로를 변경합니다.
        """
        try:
            # 폴더 선택 다이얼로그
            selected_path = filedialog.askdirectory(
                title="저장 경로 선택",
                initialdir=self.save_path
            )

            # 경로가 선택되면 업데이트
            if selected_path:
                self.save_path = selected_path
                messagebox.showinfo(
                    "경로 변경 완료",
                    f"저장 경로가 변경되었습니다.\n\n{selected_path}"
                )
                logger.info(f"저장 경로 변경: {selected_path}")

                # TODO: Config.save()로 설정 저장 (Phase 3)

        except Exception as e:
            logger.error(f"저장 경로 설정 실패: {e}")
            messagebox.showerror("오류", f"저장 경로 설정 중 오류가 발생했습니다.\n{e}")

    def _on_open_save_folder(self) -> None:
        """
        저장 폴더 열기 버튼 클릭 핸들러.

        탐색기로 저장 폴더를 엽니다.
        """
        try:
            # 폴더 존재 확인
            if not os.path.exists(self.save_path):
                messagebox.showerror(
                    "오류",
                    f"저장 폴더가 존재하지 않습니다.\n\n{self.save_path}"
                )
                logger.warning(f"저장 폴더가 존재하지 않음: {self.save_path}")
                return

            # Windows 탐색기로 폴더 열기
            os.startfile(self.save_path)
            logger.info(f"저장 폴더 열기: {self.save_path}")

        except Exception as e:
            logger.error(f"저장 폴더 열기 실패: {e}")
            messagebox.showerror("오류", f"저장 폴더 열기 중 오류가 발생했습니다.\n{e}")

    # ==================== Alert ====================

    def show_alert(self, title: str, message: str) -> None:
        """
        알림창을 표시합니다.

        TODO: Phase 2에서 캡처 성공/실패 알림에 사용

        Args:
            title: 알림창 제목
            message: 알림 메시지

        Example:
            >>> window.show_alert("캡처 성공", "1교시 캡처가 완료되었습니다.")
        """
        messagebox.showinfo(title, message)
        logger.info(f"알림 표시: {title} - {message}")
