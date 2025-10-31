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

if __name__ == "__main__":
    print("=" * 50)
    print("MainWindow 테스트 시작")
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
        print("MainWindow 테스트 정상 종료")
        print("=" * 50)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
