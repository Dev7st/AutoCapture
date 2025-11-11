"""
메인 윈도우 모듈.

출결 관리 자동 캡처 프로그램의 메인 GUI를 제공합니다.
"""

# 표준 라이브러리
import logging
import os
import platform
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Optional, Dict

# 내부 모듈
from features.capture import ScreenCapture
from features.face_detection import FaceDetector
from features.file_manager import FileManager
from features.logger import CSVLogger
from features.scheduler import CaptureScheduler

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
        capture (ScreenCapture): 화면 캡처 인스턴스
        detector (FaceDetector): 얼굴 감지 인스턴스
        file_manager (FileManager): 파일 관리 인스턴스
        scheduler (CaptureScheduler): 스케줄러 인스턴스

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
        self.root.resizable(True, True)

        # 설정값 저장
        self.config = config
        self.monitor_id: int = config.get('monitor_id', 1)
        self.save_path: str = config.get('save_path', 'C:/IBM 비대면')
        self.mode: str = config.get('mode', 'flexible')
        self.student_count: int = config.get('student_count', 1)

        # Features 인스턴스 초기화
        logger.info("Features 모듈 초기화 시작")

        # 1. ScreenCapture 인스턴스 생성
        logger.info(f"ScreenCapture 초기화 (모니터 ID: {self.monitor_id})")
        self.capture: Optional[ScreenCapture] = None
        try:
            self.capture = ScreenCapture(monitor_id=self.monitor_id)
            logger.info("ScreenCapture 초기화 완료")
        except Exception as e:
            logger.error(f"ScreenCapture 초기화 실패: {e}", exc_info=True)
            messagebox.showerror(
                "초기화 오류",
                f"화면 캡처 모듈 초기화에 실패했습니다.\n\n{e}"
            )

        # 2. FaceDetector 인스턴스 생성
        logger.info("FaceDetector 초기화 (GPU 사용 시도)")
        self.detector: Optional[FaceDetector] = None
        try:
            self.detector = FaceDetector(gpu_id=0)
            self.detector.initialize()
            logger.info("FaceDetector 초기화 완료")
        except Exception as e:
            logger.error(f"FaceDetector 초기화 실패: {e}", exc_info=True)
            messagebox.showerror(
                "초기화 오류",
                f"얼굴 감지 모듈 초기화에 실패했습니다.\n\n{e}\n\n"
                f"GPU를 사용할 수 없거나 InsightFace 모델 로드에 실패했습니다."
            )

        # 3. FileManager 인스턴스 생성
        logger.info(f"FileManager 초기화 (저장 경로: {self.save_path})")
        self.file_manager: Optional[FileManager] = None
        try:
            self.file_manager = FileManager(base_path=self.save_path)
            self.file_manager.ensure_folder_exists()
            logger.info("FileManager 초기화 완료")
        except Exception as e:
            logger.error(f"FileManager 초기화 실패: {e}", exc_info=True)
            messagebox.showerror(
                "초기화 오류",
                f"파일 관리 모듈 초기화에 실패했습니다.\n\n{e}\n\n"
                f"저장 경로를 확인하거나 폴더 권한을 확인해주세요."
            )

        # 4. CaptureScheduler 인스턴스 생성
        logger.info("CaptureScheduler 초기화")
        self.scheduler: Optional[CaptureScheduler] = None
        try:
            self.scheduler = CaptureScheduler()
            self._setup_schedules()
            logger.info("CaptureScheduler 초기화 완료")
        except Exception as e:
            logger.error(f"CaptureScheduler 초기화 실패: {e}", exc_info=True)
            messagebox.showerror(
                "초기화 오류",
                f"스케줄러 초기화에 실패했습니다.\n\n{e}"
            )

        # 5. CSVLogger 인스턴스 생성
        logger.info(f"CSVLogger 초기화 (저장 경로: {self.save_path})")
        self.csv_logger: Optional[CSVLogger] = None
        try:
            self.csv_logger = CSVLogger(base_path=self.save_path)
            logger.info("CSVLogger 초기화 완료")
        except Exception as e:
            logger.error(f"CSVLogger 초기화 실패: {e}", exc_info=True)
            messagebox.showerror(
                "초기화 오류",
                f"로그 모듈 초기화에 실패했습니다.\n\n{e}"
            )

        logger.info("Features 모듈 초기화 완료")

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

        # 윈도우 크기와 중앙 위치 설정
        self._center_window()

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

    def _setup_schedules(self) -> None:
        """
        CaptureScheduler에 교시별 스케줄을 등록합니다.

        1~8교시 + 퇴실(0) 총 9개 스케줄을 등록합니다.
        각 교시는 캡처 콜백 함수를 통해 자동 캡처를 시도합니다.
        """
        if self.scheduler is None:
            logger.warning("Scheduler가 초기화되지 않아 스케줄 등록을 건너뜁니다.")
            return

        # 1~8교시 스케줄 등록
        schedule_times = {
            1: ("09:30", "09:45"),
            2: ("10:30", "10:45"),
            3: ("11:30", "11:45"),
            4: ("12:30", "12:45"),
            5: ("14:30", "14:45"),
            6: ("15:30", "15:45"),
            7: ("16:30", "16:45"),
            8: ("17:30", "17:45"),
            0: ("18:30", "18:32"),  # 퇴실
        }

        for period, (start_time, end_time) in schedule_times.items():
            try:
                # 캡처 콜백 함수: _on_capture_trigger 메서드 호출
                def capture_callback(p=period):
                    self._on_capture_trigger(p)

                self.scheduler.add_schedule(
                    period=period,
                    start_time=start_time,
                    end_time=end_time,
                    callback=capture_callback
                )
                logger.info(f"{period}교시 스케줄 등록 완료: {start_time}~{end_time}")
            except Exception as e:
                logger.error(f"{period}교시 스케줄 등록 실패: {e}", exc_info=True)

    def _center_window(self) -> None:
        """메인 윈도우를 화면 중앙에 배치합니다."""
        # 윈도우 크기
        window_width = 900
        window_height = 1100

        # HiDPI/Retina 디스플레이 처리
        if platform.system() == "Windows":
            try:
                import ctypes
                # 실제 물리적 화면 크기 가져오기
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
            except Exception as e:
                logger.warning(f"실제 화면 크기 가져오기 실패, 기본값 사용: {e}")
                self.root.update_idletasks()
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
        else:
            # macOS, Linux는 winfo 사용
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

        # 중앙 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 크기와 위치를 함께 설정
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

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
        윈도우 종료 시 cleanup 처리를 수행합니다.
        """
        # 윈도우 종료 이벤트 핸들러 등록
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("메인 윈도우 실행 시작")
        self.root.mainloop()
        logger.info("메인 윈도우 종료")

    def _on_closing(self) -> None:
        """
        윈도우 종료 이벤트 핸들러.

        사용자가 X 버튼을 클릭하거나 윈도우를 닫을 때 호출됩니다.
        cleanup 처리를 수행한 후 윈도우를 종료합니다.
        """
        logger.info("윈도우 종료 요청 받음")

        # cleanup 처리
        self.cleanup()

        # 윈도우 파괴
        self.root.destroy()
        logger.info("윈도우 종료 완료")

    def cleanup(self) -> None:
        """
        프로그램 종료 시 리소스 정리.

        - Scheduler 중지
        - FaceDetector GPU 메모리 해제
        - 기타 리소스 정리
        """
        logger.info("=" * 60)
        logger.info("리소스 정리 시작")
        logger.info("=" * 60)

        # 1. Scheduler 중지
        if self.scheduler is not None:
            try:
                logger.info("Scheduler 중지 중...")
                self.scheduler.stop()
                logger.info("Scheduler 중지 완료")
            except Exception as e:
                logger.error(f"Scheduler 중지 실패: {e}", exc_info=True)

        # 2. FaceDetector GPU 메모리 해제
        if self.detector is not None:
            try:
                logger.info("FaceDetector GPU 메모리 해제 중...")
                self.detector.cleanup()
                logger.info("FaceDetector 메모리 해제 완료")
            except Exception as e:
                logger.error(f"FaceDetector cleanup 실패: {e}", exc_info=True)

        # 3. ScreenCapture 정리 (필요 시)
        if self.capture is not None:
            try:
                logger.info("ScreenCapture 리소스 해제")
                # ScreenCapture는 별도 cleanup 메서드가 없으므로 None 처리
                self.capture = None
            except Exception as e:
                logger.error(f"ScreenCapture 정리 실패: {e}", exc_info=True)

        # 4. FileManager 정리 (필요 시)
        if self.file_manager is not None:
            try:
                logger.info("FileManager 리소스 해제")
                # FileManager는 별도 cleanup 메서드가 없으므로 None 처리
                self.file_manager = None
            except Exception as e:
                logger.error(f"FileManager 정리 실패: {e}", exc_info=True)

        logger.info("=" * 60)
        logger.info("리소스 정리 완료")
        logger.info("=" * 60)

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

    def on_student_count_change(self, new_count: int) -> None:
        """
        출석 학생 수 변경 핸들러.

        ▲▼ 버튼 또는 직접 입력 시 호출되며,
        기준 인원을 자동으로 재계산합니다.

        Args:
            new_count: 새로운 학생 수

        Example:
            >>> window.on_student_count_change(25)
        """
        try:
            # 범위 검증
            if new_count < 1:
                new_count = 1
                self.student_count_var.set(1)
            elif new_count > 100:
                new_count = 100
                self.student_count_var.set(100)

            # 기준 인원 계산 및 레이블 업데이트
            threshold = new_count + 1
            self.threshold_label.config(
                text=f"기준 인원: {threshold}명 (학생 {new_count}명 + 강사 1명)"
            )
            logger.info(f"학생 수 변경: {new_count}명 (기준 인원: {threshold}명)")

        except Exception as e:
            logger.error(f"학생 수 변경 처리 실패: {e}")
            # 잘못된 값일 경우 기본값으로 설정
            try:
                self.student_count_var.set(1)
                self.threshold_label.config(
                    text="기준 인원: 2명 (학생 1명 + 강사 1명)"
                )
            except:
                pass

    def _update_threshold_label(self, *args) -> None:
        """
        학생 수 변경 시 기준 인원 레이블을 업데이트합니다.

        trace_add 콜백 함수로 사용됩니다.
        실제 처리는 on_student_count_change()에서 수행합니다.

        Args:
            *args: trace_add 콜백에서 전달되는 인자 (사용하지 않음)
        """
        try:
            student_count = self.student_count_var.get()
            self.on_student_count_change(student_count)
        except Exception as e:
            logger.error(f"기준 인원 레이블 업데이트 실패: {e}")

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
            # 현재 경로를 Path 객체로 변환
            initial_dir = str(Path(self.save_path))

            # 폴더 선택 다이얼로그
            selected_path = filedialog.askdirectory(
                title="저장 경로 선택",
                initialdir=initial_dir
            )

            # 경로가 선택되면 업데이트
            if selected_path:
                # Path 객체로 정규화 후 문자열로 저장
                normalized_path = str(Path(selected_path))
                self.save_path = normalized_path
                messagebox.showinfo(
                    "경로 변경 완료",
                    f"저장 경로가 변경되었습니다.\n\n{normalized_path}"
                )
                logger.info(f"저장 경로 변경: {normalized_path}")

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
            # Path 객체로 변환
            save_path_obj = Path(self.save_path)

            # 폴더 존재 확인
            if not save_path_obj.exists():
                messagebox.showerror(
                    "오류",
                    f"저장 폴더가 존재하지 않습니다.\n\n{self.save_path}"
                )
                logger.warning(f"저장 폴더가 존재하지 않음: {self.save_path}")
                return

            # Windows 탐색기로 폴더 열기 (os.startfile은 Windows 전용)
            os.startfile(str(save_path_obj))
            logger.info(f"저장 폴더 열기: {self.save_path}")

        except Exception as e:
            logger.error(f"저장 폴더 열기 실패: {e}")
            messagebox.showerror("오류", f"저장 폴더 열기 중 오류가 발생했습니다.\n{e}")

    # ==================== Private 메서드 (캡처 프로세스) ====================

    def _on_capture_trigger(self, period: int) -> None:
        """
        교시별 캡처 프로세스 실행 (Scheduler 콜백).

        Args:
            period: 교시 번호 (1~8: 교시, 0: 퇴실)

        Flow:
            1. 화면 캡처 (ScreenCapture)
            2. 얼굴 감지 (FaceDetector)
            3. 조건 비교 (모드별: 정확/유연)
            4. 성공 시: 파일 저장 → 로그 기록 → UI 업데이트 → 알림
            5. 실패 시: 메모리 해제 → 실패 로그 기록
        """
        # 교시명 생성
        period_name = f"{period}교시" if period > 0 else "퇴실"

        # UI 상태: "감지중"으로 변경
        self.update_period_status(period, "감지중")

        # 화면 캡처
        try:
            image = self.capture.capture()
        except RuntimeError as e:
            logger.error(f"{period_name} 화면 캡처 실패: {e}")
            self.csv_logger.log_event(period_name, "캡처 실패", 0, self.student_count + 1, "", str(e))
            self.show_alert("캡처 실패", f"{period_name} 화면 캡처 중 오류 발생", "error")
            return
        except Exception as e:
            logger.error(f"{period_name} 예상치 못한 오류: {e}")
            self.csv_logger.log_event(period_name, "캡처 실패", 0, self.student_count + 1, "", str(e))
            self.show_alert("오류", f"{period_name} 캡처 중 예상치 못한 오류", "error")
            return

        # 얼굴 감지
        try:
            detected_count = self.detector.detect(image)
        except ValueError as e:
            logger.error(f"{period_name} 얼굴 감지 실패: {e}")
            self.csv_logger.log_event(period_name, "감지 실패", 0, self.student_count + 1, "", str(e))
            self.show_alert("감지 실패", f"{period_name} 얼굴 감지 중 오류 발생", "error")
            del image
            return
        except Exception as e:
            logger.error(f"{period_name} 예상치 못한 오류: {e}")
            self.csv_logger.log_event(period_name, "감지 실패", 0, self.student_count + 1, "", str(e))
            self.show_alert("오류", f"{period_name} 감지 중 예상치 못한 오류", "error")
            del image
            return

        # 기준 인원 계산
        threshold = self.student_count + 1

        # 조건 확인 및 처리
        is_success, mode_note = self._check_capture_condition(detected_count, threshold)

        if is_success:
            self._process_capture_success(period, period_name, image, detected_count, threshold, mode_note)
        else:
            self._process_capture_failure(period_name, image, detected_count, threshold, mode_note)

    def _check_capture_condition(self, detected_count: int, threshold: int) -> tuple[bool, str]:
        """
        캡처 조건을 확인합니다 (모드별).

        Args:
            detected_count: 감지된 인원
            threshold: 기준 인원

        Returns:
            tuple[bool, str]: (조건 만족 여부, 모드 설명)
        """
        if self.mode == "exact":
            # 정확 모드: 감지 인원 == 기준 인원
            is_success = (detected_count == threshold)
            mode_note = "정확 모드"
        elif self.mode == "flexible":
            # 유연 모드: 감지 인원 >= 기준 인원 × 0.9
            min_required = int(threshold * 0.9)
            is_success = (detected_count >= min_required)
            mode_note = f"유연 모드 (최소 {min_required}명)"
        else:
            logger.error(f"알 수 없는 캡처 모드: {self.mode}")
            return False, "알 수 없는 모드"

        return is_success, mode_note

    def _process_capture_success(
        self,
        period: int,
        period_name: str,
        image,
        detected_count: int,
        threshold: int,
        mode_note: str
    ) -> None:
        """
        캡처 성공 시 처리 로직.

        Args:
            period: 교시 번호
            period_name: 교시명
            image: 캡처된 이미지
            detected_count: 감지된 인원
            threshold: 기준 인원
            mode_note: 모드 설명
        """
        try:
            # 1. 시간대 확인
            is_within_window = self.scheduler.is_in_capture_window(period)

            # 2. 파일 저장
            file_path = self.file_manager.save_image(image, period, is_within_window)
            file_name = Path(file_path).name

            # 3. CSV 로그 기록
            self.csv_logger.log_event(
                period_name,
                "캡처 성공",
                detected_count,
                threshold,
                file_name,
                mode_note
            )

            # 4. Scheduler 완료 처리
            self.scheduler.mark_completed(period)

            # 5. UI 업데이트
            self.update_period_status(period, "완료")

            # 6. 성공 알림창
            message = (
                f"{period_name} 캡처가 완료되었습니다.\n\n"
                f"파일: {file_name}\n"
                f"감지 인원: {detected_count}명\n"
                f"기준 인원: {threshold}명\n"
                f"모드: {mode_note}"
            )
            self.show_alert("캡처 성공", message, "info")

            logger.info(f"{period_name} 캡처 성공: {file_path}")

        except PermissionError as e:
            logger.error(f"{period_name} 파일 저장 권한 오류: {e}")
            self.csv_logger.log_event(period_name, "저장 실패", detected_count, threshold, "", "권한 오류")
            self.show_alert("저장 실패", f"{period_name} 파일 저장 권한이 없습니다.", "error")
        except OSError as e:
            logger.error(f"{period_name} 파일 저장 실패: {e}")
            self.csv_logger.log_event(period_name, "저장 실패", detected_count, threshold, "", str(e))
            self.show_alert("저장 실패", f"{period_name} 파일 저장 중 오류 발생", "error")
        except Exception as e:
            logger.error(f"{period_name} 예상치 못한 오류: {e}")
            self.csv_logger.log_event(period_name, "저장 실패", detected_count, threshold, "", str(e))
            self.show_alert("오류", f"{period_name} 저장 중 예상치 못한 오류", "error")
        finally:
            # 메모리 해제
            del image

    def _process_capture_failure(
        self,
        period_name: str,
        image,
        detected_count: int,
        threshold: int,
        mode_note: str
    ) -> None:
        """
        캡처 실패 시 처리 로직.

        Args:
            period_name: 교시명
            image: 캡처된 이미지
            detected_count: 감지된 인원
            threshold: 기준 인원
            mode_note: 모드 설명
        """
        # 1. 메모리 해제
        del image

        # 2. 실패 로그 기록
        self.csv_logger.log_event(
            period_name,
            "감지 실패",
            detected_count,
            threshold,
            "",
            f"{mode_note} - 기준 미달"
        )

        # 3. 로그만 기록 (UI는 "감지중" 유지, Scheduler가 10초 후 자동 재시도)
        logger.info(f"{period_name} 감지 실패: {detected_count}/{threshold}명")

    # ==================== Alert ====================

    def show_alert(self, title: str, message: str, alert_type: str = "info") -> None:
        """
        알림창을 표시합니다.

        캡처 성공, 실패, 에러 등 다양한 상황에서 사용자에게 알림을 제공합니다.

        Args:
            title: 알림창 제목
            message: 알림 메시지
            alert_type: 알림 타입 ("info", "warning", "error")
                - "info": 정보 알림 (성공, 완료 등)
                - "warning": 경고 알림 (실패, 재시도 필요 등)
                - "error": 에러 알림 (파일 저장 실패, 권한 오류 등)

        Example:
            >>> # 성공 알림
            >>> window.show_alert("캡처 완료", "1교시 캡처가 완료되었습니다.", "info")

            >>> # 실패 알림
            >>> window.show_alert("감지 실패", "얼굴이 감지되지 않았습니다.", "warning")

            >>> # 에러 알림
            >>> window.show_alert("저장 실패", "파일 저장 권한이 없습니다.", "error")
        """
        try:
            # alert_type에 따라 적절한 messagebox 호출
            if alert_type == "info":
                messagebox.showinfo(title, message)
            elif alert_type == "warning":
                messagebox.showwarning(title, message)
            elif alert_type == "error":
                messagebox.showerror(title, message)
            else:
                # 잘못된 타입이면 기본값 사용
                logger.warning(f"알 수 없는 alert_type: {alert_type}, info로 대체")
                messagebox.showinfo(title, message)

            logger.info(f"알림 표시: [{alert_type}] {title} - {message}")

        except Exception as e:
            logger.error(f"알림창 표시 실패: {e}", exc_info=True)
