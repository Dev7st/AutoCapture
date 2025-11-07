"""
MainWindow 테스트 스크립트.

MainWindow가 정상적으로 표시되는지 확인합니다.
"""

# 표준 라이브러리
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 내부 모듈
from gui.main_window import MainWindow

# 테스트 설정값
test_config = {
    'monitor_id': 1,
    'save_path': 'C:/IBM 비대면',
    'mode': 'flexible',
    'student_count': 1
}

def test_main_window():
    """MainWindow 기본 표시 테스트"""
    print("=" * 50)
    print("MainWindow 기본 표시 테스트")
    print("=" * 50)
    print(f"설정값: {test_config}")
    print()

    try:
        # MainWindow 생성 및 실행
        window = MainWindow(test_config)
        print("MainWindow 생성 완료")
        print("윈도우를 닫으면 프로그램이 종료됩니다.")
        print()

        window.run()

        print()
        print("=" * 50)
        print("MainWindow 기본 표시 테스트 정상 종료")
        print("=" * 50)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_alerts():
    """알림창 테스트 (Phase 1.9)"""
    print("=" * 50)
    print("알림창 테스트 시작 (Phase 1.9)")
    print("=" * 50)
    print(f"설정값: {test_config}")
    print()
    print("테스트 시나리오:")
    print("  3초 후 → 성공 알림 (info)")
    print("  6초 후 → 실패 알림 (warning)")
    print("  9초 후 → 에러 알림 (error)")
    print("  12초 후 → 자동 종료")
    print()

    try:
        window = MainWindow(test_config)
        print("MainWindow 생성 완료")
        print()

        # 3초 후: 성공 알림
        window.root.after(3000, lambda: window.show_alert(
            "캡처 성공",
            "1교시 캡처가 완료되었습니다.\n\n"
            "파일: 251107_1교시.png\n"
            "감지 인원: 22명\n"
            "기준 인원: 22명",
            alert_type="info"
        ))

        # 6초 후: 실패 알림
        window.root.after(6000, lambda: window.show_alert(
            "캡처 실패",
            "1교시 얼굴 감지 실패\n\n"
            "감지 인원: 18명\n"
            "기준 인원: 22명\n"
            "(유연 모드: 최소 20명 필요)\n\n"
            "10초 후 재시도합니다.",
            alert_type="warning"
        ))

        # 9초 후: 에러 알림
        window.root.after(9000, lambda: window.show_alert(
            "파일 저장 실패",
            "디스크 공간이 부족합니다.\n\n"
            "저장 경로를 확인해주세요.",
            alert_type="error"
        ))

        # 12초 후: 자동 종료
        window.root.after(12000, lambda: window.root.destroy())

        window.run()

        print()
        print("=" * 50)
        print("알림창 테스트 정상 종료")
        print("=" * 50)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='MainWindow 테스트')
    parser.add_argument(
        '--test',
        choices=['basic', 'alerts', 'all'],
        default='all',
        help='실행할 테스트 선택 (basic: 기본 표시, alerts: 알림창, all: 전체)'
    )
    args = parser.parse_args()

    if args.test == 'basic':
        test_main_window()
    elif args.test == 'alerts':
        test_alerts()
    elif args.test == 'all':
        print("\n[1/2] 기본 표시 테스트를 먼저 실행합니다.")
        print("윈도우를 닫으면 알림창 테스트로 넘어갑니다.\n")
        test_main_window()
        print("\n[2/2] 알림창 테스트를 시작합니다.\n")
        test_alerts()
