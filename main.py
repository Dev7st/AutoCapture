"""
출결 관리 자동 캡처 프로그램 진입점.

이 모듈은 프로그램의 메인 진입점으로, 다음 순서로 실행됩니다:
1. 초기 설정 다이얼로그 표시 (InitDialog)
2. 사용자 설정 수집 (monitor, save_path, mode, student_count)
3. 메인 윈도우 실행 (MainWindow)
4. Features 모듈 초기화 및 스케줄링 시작
5. 프로그램 종료 시 cleanup 처리

Usage:
    python main.py
"""

# 표준 라이브러리
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 내부 모듈
from gui.dialogs import InitDialog
from gui.main_window import MainWindow


def main() -> None:
    """
    프로그램 메인 함수.

    1. InitDialog를 표시하여 사용자 설정 수집
    2. 설정값 검증
    3. MainWindow 실행

    Raises:
        Exception: 프로그램 실행 중 치명적 오류 발생 시
    """
    try:
        logger.info("=" * 60)
        logger.info("출결 관리 자동 캡처 프로그램 시작")
        logger.info("=" * 60)

        # 1. 초기 설정 다이얼로그 표시
        logger.info("초기 설정 다이얼로그 표시")
        dialog = InitDialog()
        config = dialog.show()

        # 사용자가 취소를 선택한 경우
        if config is None:
            logger.info("사용자가 초기 설정을 취소했습니다. 프로그램을 종료합니다.")
            return

        # 설정값 로깅
        logger.info("초기 설정 완료:")
        logger.info(f"  - 모니터 ID: {config.get('monitor_id')}")
        logger.info(f"  - 저장 경로: {config.get('save_path')}")
        logger.info(f"  - 캡처 모드: {config.get('mode')}")
        logger.info(f"  - 학생 수: {config.get('student_count')}명")

        # 2. 메인 윈도우 생성 및 실행
        logger.info("메인 윈도우 시작")
        window = MainWindow(config)
        window.run()

        logger.info("=" * 60)
        logger.info("프로그램 정상 종료")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n사용자가 프로그램을 중단했습니다.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"치명적 오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
