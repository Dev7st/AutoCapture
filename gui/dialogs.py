"""
초기 설정 다이얼로그 모듈.

사용자로부터 초기 설정값을 입력받는 다이얼로그를 제공합니다.
"""

# 표준 라이브러리
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict


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
        # TODO: UI 요소들을 순차적으로 추가할 예정
        pass

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
        # TODO: 결과 dict 생성 및 저장
        self.result = {}
        self.dialog.destroy()

    def on_cancel(self) -> None:
        """
        취소 버튼 클릭 핸들러.

        입력을 취소하고 다이얼로그를 닫습니다.
        결과는 None으로 설정됩니다.
        """
        self.result = None
        self.dialog.destroy()
