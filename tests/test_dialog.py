"""
InitDialog 수동 테스트 스크립트.

InitDialog를 실행하고 사용자 입력 결과를 콘솔에 출력합니다.
"""

# 표준 라이브러리
import sys
from pathlib import Path
import tkinter as tk

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 내부 모듈
from gui.dialogs import InitDialog


def main():
    """
    InitDialog 테스트를 실행합니다.
    """
    print("=" * 50)
    print("InitDialog 테스트 시작")
    print("=" * 50)
    print()
    print("[테스트 시나리오]")
    print("1. 모든 값 정상 입력 -> [시작] 클릭")
    print("2. 학생 수 0 입력 -> [시작] 클릭 (에러 확인)")
    print("3. 학생 수 101 입력 -> [시작] 클릭 (에러 확인)")
    print("4. 저장 경로 비우기 -> [시작] 클릭 (에러 확인)")
    print("5. [취소] 버튼 클릭 (None 반환 확인)")
    print()
    print("-" * 50)
    print()

    # tkinter 루트 윈도우 생성
    root = tk.Tk()

    # InitDialog 실행
    dialog = InitDialog(root)
    result = dialog.show()

    # 결과 출력
    print()
    print("=" * 50)
    print("테스트 결과")
    print("=" * 50)
    print()

    if result is None:
        print("[X] 취소됨 (result = None)")
    else:
        print("[O] 설정 완료!")
        print()
        print("[반환된 dict]")
        print(f"  - monitor_id    : {result['monitor_id']} (타입: {type(result['monitor_id']).__name__})")
        print(f"  - save_path     : {result['save_path']} (타입: {type(result['save_path']).__name__})")
        print(f"  - mode          : {result['mode']} (타입: {type(result['mode']).__name__})")
        print(f"  - student_count : {result['student_count']} (타입: {type(result['student_count']).__name__})")
        print()
        print(f"[기준 인원] {result['student_count'] + 1}명 (학생 {result['student_count']}명 + 교사 1명)")

    print()
    print("=" * 50)
    print("테스트 종료")
    print("=" * 50)

    # 윈도우 정리
    root.destroy()


if __name__ == "__main__":
    main()
