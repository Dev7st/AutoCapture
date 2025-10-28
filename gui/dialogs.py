"""
초기 설정 다이얼로그 모듈.

사용자로부터 초기 설정값을 입력받는 다이얼로그를 제공합니다.
"""

# 표준 라이브러리
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, List

# 내부 모듈
from utils.monitor import get_monitor_names, get_monitor_count


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
        {'monitor_id': 2, 'save_path': 'C:/IBM 비대면', 'mode': 'flexible', 'student_count': 21}
    """

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
        self.dialog.geometry("400x500")
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
        main_frame = ttk.Frame(self.dialog, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 모니터 선택 영역
        self._create_monitor_section(main_frame)

        # TODO: 2. 저장 경로 선택 영역 (다음 단계)
        # TODO: 3. 캡처 모드 선택 영역 (다음 단계)
        # TODO: 4. 출석 학생 수 입력 영역 (다음 단계)
        # TODO: 5. 확인/취소 버튼 영역 (다음 단계)

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
            padding="10 10 10 10"
        )
        section_frame.pack(fill=tk.X, pady=(0, 10))

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
            text=f"감지된 모니터: {monitor_count}개"
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))

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
            width=30
        )
        monitor_combo.pack(anchor=tk.W, pady=(0, 5))

        # 안내 텍스트
        help_label = ttk.Label(
            section_frame,
            text="Zoom 화면이 표시되는 모니터를 선택하세요.",
            font=("", 8),
            foreground="gray"
        )
        help_label.pack(anchor=tk.W)

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

    def on_ok(self) -> None:
        """
        확인 버튼 클릭 핸들러.

        입력값을 검증하고, 유효한 경우 결과를 저장한 후
        다이얼로그를 닫습니다.
        """
        # TODO: 입력값 검증 로직 추가 예정

        # 선택된 모니터 ID 추출
        monitor_id = self._get_selected_monitor_id()

        # 결과 dict 생성 및 저장
        self.result = {
            'monitor_id': monitor_id,
            # TODO: 나머지 설정값 추가 예정
            'save_path': None,
            'mode': None,
            'student_count': None
        }
        self.dialog.destroy()

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

    def on_cancel(self) -> None:
        """
        취소 버튼 클릭 핸들러.

        입력을 취소하고 다이얼로그를 닫습니다.
        결과는 None으로 설정됩니다.
        """
        self.result = None
        self.dialog.destroy()
