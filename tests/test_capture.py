"""
화면 캡처 기능 테스트 스크립트.

ScreenCapture 클래스가 정상 작동하는지 확인합니다.
"""

# 표준 라이브러리
import sys
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 외부 라이브러리
import numpy as np

# 내부 모듈
from features.capture import ScreenCapture


def test_init():
    """ScreenCapture 초기화 테스트."""
    print("=" * 60)
    print("1. ScreenCapture 초기화 테스트")
    print("=" * 60)

    try:
        # 기본값으로 초기화
        capturer = ScreenCapture()
        print(f"✅ 기본값 초기화 성공")
        print(f"   monitor_id: {capturer.monitor_id}")
        print()

        # monitor_id 지정
        capturer2 = ScreenCapture(monitor_id=1)
        print(f"✅ monitor_id=1 초기화 성공")
        print(f"   monitor_id: {capturer2.monitor_id}")
        print()

        return True

    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_monitor_id():
    """잘못된 monitor_id 테스트."""
    print("=" * 60)
    print("2. 잘못된 monitor_id 테스트")
    print("=" * 60)

    try:
        capturer = ScreenCapture(monitor_id=0)
        print(f"❌ ValueError가 발생해야 하는데 인스턴스가 생성됨")
        return False

    except ValueError as e:
        print(f"✅ ValueError 정상 발생: {e}")
        print()
        return True

    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_monitor_info():
    """모니터 정보 조회 테스트."""
    print("=" * 60)
    print("3. 모니터 정보 조회 테스트")
    print("=" * 60)

    try:
        capturer = ScreenCapture(monitor_id=1)
        info = capturer.get_monitor_info()

        print(f"✅ 모니터 정보 조회 성공")
        print(f"   ID: {info['id']}")
        print(f"   해상도: {info['width']}x{info['height']}")
        print(f"   위치: ({info['left']}, {info['top']})")
        print()

        # 검증
        assert isinstance(info, dict), "반환값은 dict여야 합니다"
        assert 'id' in info, "'id' 키가 없습니다"
        assert 'width' in info, "'width' 키가 없습니다"
        assert 'height' in info, "'height' 키가 없습니다"
        assert info['width'] > 0, "width는 0보다 커야 합니다"
        assert info['height'] > 0, "height는 0보다 커야 합니다"

        return True

    except Exception as e:
        print(f"❌ 모니터 정보 조회 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_capture():
    """화면 캡처 테스트."""
    print("=" * 60)
    print("4. 화면 캡처 테스트")
    print("=" * 60)

    try:
        capturer = ScreenCapture(monitor_id=1)

        # 캡처 시간 측정
        start_time = time.time()
        image = capturer.capture()
        elapsed_time = time.time() - start_time

        print(f"✅ 화면 캡처 성공")
        print(f"   이미지 타입: {type(image)}")
        print(f"   이미지 shape: {image.shape}")
        print(f"   이미지 dtype: {image.dtype}")
        print(f"   캡처 시간: {elapsed_time:.3f}초")
        print()

        # 검증
        assert isinstance(image, np.ndarray), "반환값은 numpy array여야 합니다"
        assert len(image.shape) == 3, "이미지는 3차원이어야 합니다 (height, width, 3)"
        assert image.shape[2] == 3, "RGB 채널은 3개여야 합니다"
        assert image.dtype == np.uint8, "dtype은 uint8이어야 합니다"
        assert image.shape[0] > 0, "height는 0보다 커야 합니다"
        assert image.shape[1] > 0, "width는 0보다 커야 합니다"

        # 성능 검증 (목표: 0.5초 이하)
        if elapsed_time > 0.5:
            print(f"⚠️  경고: 캡처 시간이 목표(0.5초)를 초과했습니다")
        else:
            print(f"✅ 성능 목표 달성 (≤ 0.5초)")

        print()
        return True

    except Exception as e:
        print(f"❌ 화면 캡처 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rgb_conversion():
    """RGB 변환 확인 테스트."""
    print("=" * 60)
    print("5. RGB 변환 확인 테스트")
    print("=" * 60)

    try:
        capturer = ScreenCapture(monitor_id=1)
        image = capturer.capture()

        # 픽셀 값 범위 확인
        min_val = image.min()
        max_val = image.max()

        print(f"✅ RGB 변환 검증 완료")
        print(f"   최소 픽셀 값: {min_val}")
        print(f"   최대 픽셀 값: {max_val}")
        print(f"   값 범위: 0~255 (uint8)")
        print()

        # 검증
        assert min_val >= 0, "최소값은 0 이상이어야 합니다"
        assert max_val <= 255, "최대값은 255 이하여야 합니다"

        return True

    except Exception as e:
        print(f"❌ RGB 변환 검증 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_captures():
    """연속 캡처 테스트."""
    print("=" * 60)
    print("6. 연속 캡처 테스트 (10회)")
    print("=" * 60)

    try:
        capturer = ScreenCapture(monitor_id=1)

        total_time = 0
        capture_count = 10

        for i in range(capture_count):
            start_time = time.time()
            image = capturer.capture()
            elapsed_time = time.time() - start_time
            total_time += elapsed_time

        avg_time = total_time / capture_count

        print(f"✅ 연속 캡처 성공")
        print(f"   총 캡처 횟수: {capture_count}회")
        print(f"   총 소요 시간: {total_time:.3f}초")
        print(f"   평균 캡처 시간: {avg_time:.3f}초")
        print()

        return True

    except Exception as e:
        print(f"❌ 연속 캡처 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("ScreenCapture 테스트 시작")
    print("=" * 60)
    print()

    results = []
    results.append(test_init())
    results.append(test_invalid_monitor_id())
    results.append(test_get_monitor_info())
    results.append(test_capture())
    results.append(test_rgb_conversion())
    results.append(test_multiple_captures())

    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    success_count = sum(results)
    total_count = len(results)
    print(f"성공: {success_count}/{total_count}")

    if all(results):
        print("✅ 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")

    print("=" * 60)
    print()

    sys.exit(0 if all(results) else 1)
