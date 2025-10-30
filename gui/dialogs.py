"""
초기 설정 다이얼로그 모듈.

사용자로부터 초기 설정값을 입력받는 다이얼로그를 제공합니다.
"""

# 표준 라이브러리
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, List

# 내부 모듈
from utils.monitor import get_monitor_names, get_monitor_count

# 로거 설정
logger = logging.getLogger(__name__)


class InitDialog:
    """
    초기 설정 다이얼로그 클래스.

    프로그램 시작 시 사용자로부터 다음 설정을 입력받습니다:
    - 캡처 모니터 선택
    - 저장 경로 설정
    - 캡처 모드 선택 (정확/유연)
    - 출석 학생 수 입력

    Attributes:
        parent: 부모 윈도우
        dialog (tk.Toplevel): 다이얼로그 윈도우
        result (Optional[Dict]): 사용자 입력 결과

    Example:
        >>> dialog = InitDialog(parent)
        >>> result = dialog.show()
        >>> print(result)
        {'monitor_id': 2, 'save_path': 'C:/IBM 비대면', 'mode': 'flexible', 'student_count': 1}
    """

    # ==================== Public Methods ====================

    def __init__(self, parent: tk.Tk):
        """
        초기 설정 다이얼로그를 초기화합니다.

        Args:
            parent: 부모 윈도우
        """
        self.parent = parent
        self.dialog: Optional[tk.Toplevel] = None
        self.result: Optional[Dict] = None

        # UI 변수
        self.monitor_var: Optional[tk.StringVar] = None
        self.monitor_names: List[str] = []
        self.save_path_var: Optional[tk.StringVar] = None
        self.mode_var: Optional[tk.StringVar] = None
        self.student_count_var: Optional[tk.IntVar] = None

    def show(self) -> Optional[Dict]:
        """
        다이얼로그를 표시하고 사용자 입력을 받습니다.

        모달 다이얼로그로 표시되며, 사용자가 확인 또는 취소를
        선택할 때까지 대기합니다.

        Returns:
            Optional[Dict]: 사용자가 입력한 설정값.
                           취소 시 None 반환.
                           {
                               'monitor_id': int,      # 모니터 ID (1, 2, ...)
                               'save_path': str,       # 저장 경로
                               'mode': str,            # 'exact' or 'flexible'
                               'student_count': int    # 학생 수
                           }

        Example:
            >>> dialog = InitDialog(parent)
            >>> result = dialog.show()
            >>> if result:
            ...     print(f"선택된 모니터: {result['monitor_id']}")
        """
        # 다이얼로그 윈도우 생성
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("초기 설정")
        self.dialog.geometry("850x1250")
        self.dialog.resizable(False, False)

        # 모달 설정 (부모 윈도우 비활성화)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # UI 구성 (다음 단계에서 구현)
        self._setup_ui()

        # 윈도우 중앙 배치
        self._center_window()

        # 다이얼로그가 닫힐 때까지 대기
        self.dialog.wait_window()

        return self.result

    # ==================== UI Setup ====================

    def _setup_ui(self) -> None:
        """
        UI 구성요소를 배치합니다.

        다음 단계에서 각 UI 요소를 순차적으로 추가할 예정입니다:
        1. 모니터 선택
        2. 저장 경로 선택
        3. 캡처 모드 선택
        4. 출석 학생 수 입력
        5. 확인/취소 버튼
        """
        # 메인 프레임 (패딩 추가)
        main_frame = ttk.Frame(self.dialog, padding="60 60 60 60")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 모니터 선택 영역
        self._create_monitor_section(main_frame)

        # 2. 저장 경로 선택 영역
        self._create_save_path_section(main_frame)

        # 3. 캡처 모드 선택 영역
        self._create_mode_section(main_frame)

        # 4. 출석 학생 수 입력 영역
        self._create_student_count_section(main_frame)

        # 5. 확인/취소 버튼 영역
        self._create_button_section(main_frame)

    def _center_window(self) -> None:
        """다이얼로그를 화면 중앙에 배치합니다."""
        self.dialog.update_idletasks()

        # 화면 크기
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # 윈도우 크기
        window_width = self.dialog.winfo_width()
        window_height = self.dialog.winfo_height()

        # 중앙 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    # ==================== Monitor Section ====================

    def _create_monitor_section(self, parent: ttk.Frame) -> None:
        """
        모니터 선택 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="캡처 모니터 선택",
            padding="30 30 30 30"
        )
        # LabelFrame 제목 폰트 설정
        section_frame.configure(labelwidget=ttk.Label(parent, text="캡처 모니터 선택", font=("", 16, "bold")))
        section_frame.pack(fill=tk.X, pady=(0, 50))

        # 모니터 목록 조회
        try:
            self.monitor_names = get_monitor_names()
            monitor_count = get_monitor_count()

            if monitor_count == 0:
                # 모니터 감지 실패
                error_label = ttk.Label(
                    section_frame,
                    text="⚠️ 모니터를 감지할 수 없습니다.",
                    foreground="red"
                )
                error_label.pack()
                return

        except Exception as e:
            # 예외 발생 시 에러 메시지
            logger.error(f"모니터 조회 실패: {e}")
            error_label = ttk.Label(
                section_frame,
                text=f"⚠️ 모니터 조회 실패: {e}",
                foreground="red"
            )
            error_label.pack()
            return

        # 모니터 선택 레이블
        info_label = ttk.Label(
            section_frame,
            text=f"감지된 모니터: {monitor_count}개",
            font=("", 18)
        )
        info_label.pack(anchor=tk.W, pady=(0, 20))

        # 모니터 선택 콤보박스
        self.monitor_var = tk.StringVar()

        # 기본값: 첫 번째 모니터 (모니터 1)
        if self.monitor_names:
            self.monitor_var.set(self.monitor_names[0])

        monitor_combo = ttk.Combobox(
            section_frame,
            textvariable=self.monitor_var,
            values=self.monitor_names,
            state="readonly",
            width=30,
            font=("", 16)
        )
        monitor_combo.pack(anchor=tk.W, pady=(0, 20))

        # 안내 텍스트
        help_label = ttk.Label(
            section_frame,
            text="Zoom 화면이 표시되는 모니터를 선택하세요.",
            font=("", 14),
            foreground="gray"
        )
        help_label.pack(anchor=tk.W)

    def _get_selected_monitor_id(self) -> int:
        """
        선택된 모니터의 ID를 반환합니다.

        "모니터 1", "모니터 2" 형식에서 숫자를 추출합니다.

        Returns:
            int: 모니터 ID (기본값: 1)

        Example:
            >>> # monitor_var.get() == "모니터 2"
            >>> id = self._get_selected_monitor_id()
            >>> print(id)
            2
        """
        if not self.monitor_var:
            return 1

        try:
            # "모니터 1" -> 1 추출
            monitor_name = self.monitor_var.get()
            monitor_id = int(monitor_name.split()[-1])
            return monitor_id
        except (ValueError, IndexError):
            # 파싱 실패 시 기본값 1 반환
            return 1

    # ==================== Save Path Section ====================

    def _create_save_path_section(self, parent: ttk.Frame) -> None:
        """
        저장 경로 선택 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="저장 경로 선택",
            padding="30 30 30 30"
        )
        # LabelFrame 제목 폰트 설정
        section_frame.configure(labelwidget=ttk.Label(parent, text="저장 경로 선택", font=("", 16, "bold")))
        section_frame.pack(fill=tk.X, pady=(0, 50))

        # 경로 입력 영역 (Entry + Button)
        path_frame = ttk.Frame(section_frame)
        path_frame.pack(fill=tk.X, pady=(0, 20))

        # 저장 경로 변수 초기화 (기본값: C:/IBM 비대면)
        self.save_path_var = tk.StringVar(value="C:/IBM 비대면")

        # 경로 입력 필드
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.save_path_var,
            width=30,
            font=("", 16)
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        # [찾아보기...] 버튼
        browse_button = ttk.Button(
            path_frame,
            text="찾아보기...",
            command=self._browse_directory
        )
        browse_button.pack(side=tk.LEFT)

        # 안내 텍스트
        help_label = ttk.Label(
            section_frame,
            text="캡처한 이미지를 저장할 폴더를 선택하세요.",
            font=("", 14),
            foreground="gray"
        )
        help_label.pack(anchor=tk.W)

    def _browse_directory(self) -> None:
        """
        폴더 선택 다이얼로그를 표시하고 선택된 경로를 업데이트합니다.
        """
        try:
            # 현재 경로를 초기 디렉토리로 설정
            initial_dir = self.save_path_var.get() if self.save_path_var else "C:/"

            # 폴더 선택 다이얼로그 표시
            selected_path = filedialog.askdirectory(
                title="저장 경로 선택",
                initialdir=initial_dir
            )

            # 경로가 선택되면 업데이트 (취소 시 빈 문자열 반환)
            if selected_path:
                self.save_path_var.set(selected_path)

        except Exception as e:
            # 예외 발생 시 에러 로그 및 사용자 알림
            logger.error(f"폴더 선택 다이얼로그 실패: {e}")
            messagebox.showerror(
                "오류",
                f"폴더 선택 중 오류가 발생했습니다.\n{e}"
            )

    # ==================== Mode Section ====================

    def _create_mode_section(self, parent: ttk.Frame) -> None:
        """
        캡처 모드 선택 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="캡처 모드 선택",
            padding="30 30 30 30"
        )
        # LabelFrame 제목 폰트 설정
        section_frame.configure(labelwidget=ttk.Label(parent, text="캡처 모드 선택", font=("", 16, "bold")))
        section_frame.pack(fill=tk.X, pady=(0, 50))

        # 모드 변수 초기화 (기본값: flexible - 유연 모드)
        self.mode_var = tk.StringVar(value="flexible")

        # 정확 모드 라디오 버튼
        # ttk.Radiobutton은 font를 직접 지원하지 않으므로 tk.Radiobutton 사용
        # 배경색을 시스템 기본 버튼 배경색으로 설정
        exact_radio = tk.Radiobutton(
            section_frame,
            text="정확 모드",
            variable=self.mode_var,
            value="exact",
            font=("", 16),
            bg="#f0f0f0",
            activebackground="#f0f0f0",
            highlightthickness=0,
            borderwidth=0
        )
        exact_radio.pack(anchor=tk.W, pady=(0, 12))

        # 정확 모드 설명
        exact_desc = ttk.Label(
            section_frame,
            text="  → 얼굴 감지 정확도 우선 (느림, 높은 정확도)",
            font=("", 14),
            foreground="gray"
        )
        exact_desc.pack(anchor=tk.W, pady=(0, 25))

        # 유연 모드 라디오 버튼
        flexible_radio = tk.Radiobutton(
            section_frame,
            text="유연 모드 (권장)",
            variable=self.mode_var,
            value="flexible",
            font=("", 16),
            bg="#f0f0f0",
            activebackground="#f0f0f0",
            highlightthickness=0,
            borderwidth=0
        )
        flexible_radio.pack(anchor=tk.W, pady=(0, 12))

        # 유연 모드 설명
        flexible_desc = ttk.Label(
            section_frame,
            text="  → 속도와 정확도 균형 (빠름, 충분한 정확도)",
            font=("", 14),
            foreground="gray"
        )
        flexible_desc.pack(anchor=tk.W)

    # ==================== Student Count Section ====================

    def _create_student_count_section(self, parent: ttk.Frame) -> None:
        """
        출석 학생 수 입력 UI를 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 섹션 프레임
        section_frame = ttk.LabelFrame(
            parent,
            text="출석 학생 수",
            padding="30 30 30 30"
        )
        # LabelFrame 제목 폰트 설정
        section_frame.configure(labelwidget=ttk.Label(parent, text="출석 학생 수", font=("", 16, "bold")))
        section_frame.pack(fill=tk.X, pady=(0, 50))

        # 학생 수 변수 초기화 (기본값: 1명)
        self.student_count_var = tk.IntVar(value=1)

        # 입력 영역 생성
        self._create_count_input_area(section_frame)

        # 기준 인원 표시 영역 생성
        self._create_threshold_display(section_frame)

        # 안내 텍스트
        help_label = ttk.Label(
            section_frame,
            text="출석한 학생 수를 입력하세요. (1~100명)",
            font=("", 14),
            foreground="gray"
        )
        help_label.pack(anchor=tk.W)

    def _create_count_input_area(self, parent: ttk.LabelFrame) -> None:
        """
        학생 수 입력 영역을 생성합니다 (Entry + ▲▼ 버튼).

        Args:
            parent: 부모 프레임
        """
        # 입력 영역 (Entry + 버튼)
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # 안내 레이블
        label = ttk.Label(input_frame, text="학생 수:", font=("", 18))
        label.pack(side=tk.LEFT, padx=(0, 15))

        # 학생 수 입력 필드
        count_entry = ttk.Entry(
            input_frame,
            textvariable=self.student_count_var,
            width=10,
            justify=tk.CENTER,
            font=("", 18)
        )
        count_entry.pack(side=tk.LEFT, padx=(0, 15))

        # ▲ 버튼 (+1)
        up_button = ttk.Button(
            input_frame,
            text="▲",
            width=3,
            command=self._increment_student_count
        )
        up_button.pack(side=tk.LEFT, padx=(0, 8))

        # ▼ 버튼 (-1)
        down_button = ttk.Button(
            input_frame,
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
        # 기준 인원 표시 Label (학생 수 + 1)
        self.threshold_label = ttk.Label(
            parent,
            text=f"기준 인원: {self.student_count_var.get() + 1}명 (학생 수 + 교사 1명)",
            font=("", 16),
            foreground="blue"
        )
        self.threshold_label.pack(anchor=tk.W, pady=(0, 20))

        # 학생 수 변경 시 기준 인원 자동 업데이트
        self.student_count_var.trace_add("write", self._update_threshold_label)

    def _increment_student_count(self) -> None:
        """
        학생 수를 1 증가시킵니다.

        최대값 100을 초과하지 않도록 제한합니다.
        """
        current_value = self.student_count_var.get()
        if current_value < 100:
            self.student_count_var.set(current_value + 1)

    def _decrement_student_count(self) -> None:
        """
        학생 수를 1 감소시킵니다.

        최소값 1 미만으로 내려가지 않도록 제한합니다.
        """
        current_value = self.student_count_var.get()
        if current_value > 1:
            self.student_count_var.set(current_value - 1)

    def _update_threshold_label(self, *args) -> None:
        """
        학생 수가 변경될 때 기준 인원 레이블을 업데이트합니다.

        Args:
            *args: trace_add 콜백에서 전달되는 인자 (사용하지 않음)
        """
        try:
            current_count = self.student_count_var.get()
            threshold = current_count + 1
            self.threshold_label.config(
                text=f"기준 인원: {threshold}명 (학생 수 + 교사 1명)"
            )
        except Exception as e:
            # 입력값이 정수가 아닌 경우 에러 로그
            logger.error(f"학생 수 입력값 오류: {e}")

    # ==================== Button Section ====================

    def _create_button_section(self, parent: ttk.Frame) -> None:
        """
        확인/취소 버튼 영역을 생성합니다.

        Args:
            parent: 부모 프레임
        """
        # 버튼 영역 프레임
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(60, 0))

        # 버튼 스타일 설정
        style = ttk.Style()
        # padding: (left, top, right, bottom) - 위 패딩을 줄여서 텍스트를 중앙으로
        style.configure("Large.TButton", font=("", 16, "bold"), padding=(15, 8, 15, 8))

        # 취소 버튼
        cancel_button = ttk.Button(
            button_frame,
            text="취소",
            width=18,
            command=self.on_cancel,
            style="Large.TButton"
        )
        cancel_button.pack(side=tk.RIGHT, padx=(15, 0))

        # 시작 버튼
        ok_button = ttk.Button(
            button_frame,
            text="시작",
            width=18,
            command=self.on_ok,
            style="Large.TButton"
        )
        ok_button.pack(side=tk.RIGHT)

    # ==================== Validation ====================

    def _validate_inputs(self) -> bool:
        """
        사용자 입력값의 유효성을 검증합니다.

        Returns:
            bool: 모든 입력이 유효하면 True, 그렇지 않으면 False

        Validation Rules:
            - 학생 수: 1~100 범위
            - 저장 경로: 비어있지 않음
            - 모니터: 선택됨
        """
        # 1. 학생 수 검증 (1~100)
        try:
            student_count = self.student_count_var.get()
            if student_count < 1 or student_count > 100:
                messagebox.showerror(
                    "입력 오류",
                    "학생 수는 1~100명 사이여야 합니다."
                )
                return False
        except Exception as e:
            logger.error(f"학생 수 검증 실패: {e}")
            messagebox.showerror(
                "입력 오류",
                "학생 수가 올바르지 않습니다."
            )
            return False

        # 2. 저장 경로 검증 (비어있지 않음)
        save_path = self.save_path_var.get() if self.save_path_var else ""
        if not save_path or save_path.strip() == "":
            messagebox.showerror(
                "입력 오류",
                "저장 경로를 선택해주세요."
            )
            return False

        # 3. 모니터 선택 검증
        if not self.monitor_var or not self.monitor_var.get():
            messagebox.showerror(
                "입력 오류",
                "캡처 모니터를 선택해주세요."
            )
            return False

        # 모든 검증 통과
        return True

    # ==================== Event Handlers ====================

    def on_ok(self) -> None:
        """
        확인 버튼 클릭 핸들러.

        입력값을 검증하고, 유효한 경우 결과를 저장한 후
        다이얼로그를 닫습니다.
        """
        # 입력값 검증
        if not self._validate_inputs():
            # 검증 실패 시 다이얼로그 유지 (early return)
            return

        # 선택된 모니터 ID 추출
        monitor_id = self._get_selected_monitor_id()

        # 저장 경로 가져오기
        save_path = self.save_path_var.get() if self.save_path_var else "C:/IBM 비대면"

        # 캡처 모드 가져오기
        mode = self.mode_var.get() if self.mode_var else "flexible"

        # 학생 수 가져오기
        student_count = self.student_count_var.get() if self.student_count_var else 1

        # 결과 dict 생성 및 저장
        self.result = {
            'monitor_id': monitor_id,
            'save_path': save_path,
            'mode': mode,
            'student_count': student_count
        }
        self.dialog.destroy()

    def on_cancel(self) -> None:
        """
        취소 버튼 클릭 핸들러.

        입력을 취소하고 다이얼로그를 닫습니다.
        결과는 None으로 설정됩니다.
        """
        self.result = None
        self.dialog.destroy()
