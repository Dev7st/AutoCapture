"""
모니터 감지 기능 테스트 스크립트.

듀얼 모니터 환경에서 모니터 감지 기능이 정상 작동하는지 확인합니다.
"""

# 표준 라이브러리
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 내부 모듈
from utils.monitor import get_monitors, get_monitor_count, get_monitor_names


def test_monitor_detection():
    """모니터 감지 기능을 테스트합니다."""
    print("=" * 60)
    print("모니터 감지 테스트 시작")
    print("=" * 60)
    print()

    # 1. 모니터 개수 확인
    print("1. 모니터 개수 확인")
    print("-" * 60)
    count = get_monitor_count()
    print(f"감지된 모니터 개수: {count}개")
    print()

    if count == 0:
        print("⚠️  경고: 모니터가 감지되지 않았습니다!")
        print("   mss 라이브러리 설치 또는 시스템 설정을 확인하세요.")
        return False

    # 2. 모니터 상세 정보 확인
    print("2. 모니터 상세 정보")
    print("-" * 60)
    monitors = get_monitors()

    for monitor in monitors:
        print(f"ID: {monitor['id']}")
        print(f"이름: {monitor['name']}")
        print(f"해상도: {monitor['width']}x{monitor['height']}")
        print(f"위치: ({monitor['left']}, {monitor['top']})")
        print()

    # 3. 모니터 이름 목록 확인
    print("3. 모니터 이름 목록 (UI용)")
    print("-" * 60)
    names = get_monitor_names()
    print(f"모니터 이름 리스트: {names}")
    print()

    # 4. 듀얼 모니터 환경 확인
    print("4. 듀얼 모니터 환경 확인")
    print("-" * 60)
    if count >= 2:
        print("✅ 듀얼 모니터 환경이 감지되었습니다!")
        print(f"   - 주 모니터: {monitors[0]['name']} ({monitors[0]['width']}x{monitors[0]['height']})")
        print(f"   - 보조 모니터: {monitors[1]['name']} ({monitors[1]['width']}x{monitors[1]['height']})")
    elif count == 1:
        print("⚠️  단일 모니터 환경입니다.")
        print("   듀얼 모니터 기능은 모니터가 2개 이상일 때 테스트 가능합니다.")
    print()

    # 5. 테스트 결과 요약
    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"✅ 모니터 감지: 성공 ({count}개)")
    print(f"✅ 모니터 정보 조회: 성공")
    print(f"✅ 모니터 이름 목록: 성공")

    if count >= 2:
        print(f"✅ 듀얼 모니터 지원: 가능")
    else:
        print(f"⚠️  듀얼 모니터 지원: 단일 모니터 환경")

    print()
    print("=" * 60)
    print("테스트 완료!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_monitor_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
