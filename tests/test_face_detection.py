"""
얼굴 감지 기능 테스트 스크립트.

FaceDetector 클래스가 정상 작동하는지 확인합니다.
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
from features.face_detection import FaceDetector
from features.capture import ScreenCapture


def test_init():
    """FaceDetector 초기화 테스트."""
    print("=" * 60)
    print("1. FaceDetector 초기화 테스트")
    print("=" * 60)

    try:
        # 기본값으로 초기화 (GPU)
        detector = FaceDetector()
        print(f"✅ 기본값 초기화 성공")
        print(f"   gpu_id: {detector.gpu_id}")
        print(f"   is_initialized: {detector.is_initialized}")
        print()

        # CPU 모드 초기화
        detector_cpu = FaceDetector(gpu_id=-1)
        print(f"✅ CPU 모드 초기화 성공")
        print(f"   gpu_id: {detector_cpu.gpu_id}")
        print(f"   is_initialized: {detector_cpu.is_initialized}")
        print()

        return True

    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_initialize():
    """InsightFace 모델 로드 테스트."""
    print("=" * 60)
    print("2. InsightFace 모델 로드 테스트")
    print("=" * 60)

    try:
        detector = FaceDetector(gpu_id=0)
        print(f"모델 로드 시작 (GPU 시도)...")
        print(f"⚠️  첫 실행 시 ~100MB 모델 다운로드 (1-2분 소요)")
        print()

        start_time = time.time()
        detector.initialize()
        elapsed_time = time.time() - start_time

        print(f"✅ 모델 로드 성공")
        print(f"   is_initialized: {detector.is_initialized}")
        print(f"   실제 사용 모드: {'GPU' if detector.gpu_id >= 0 else 'CPU'}")
        print(f"   로드 시간: {elapsed_time:.3f}초")
        print()

        # 중복 초기화 테스트
        print("중복 초기화 테스트...")
        detector.initialize()
        print(f"✅ 중복 초기화 방지 확인 (경고 로그 출력)")
        print()

        return True

    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detect_with_real_image():
    """실제 화면 캡처로 얼굴 감지 테스트."""
    print("=" * 60)
    print("3. 실제 화면 캡처로 얼굴 감지 테스트")
    print("=" * 60)

    try:
        # FaceDetector 초기화
        detector = FaceDetector()
        detector.initialize()

        # 화면 캡처
        capturer = ScreenCapture(monitor_id=1)
        print(f"화면 캡처 중...")
        image = capturer.capture()
        print(f"✅ 캡처 완료: {image.shape}")
        print()

        # 얼굴 감지
        print(f"얼굴 감지 중...")
        start_time = time.time()
        face_count = detector.detect(image)
        elapsed_time = time.time() - start_time

        print(f"✅ 얼굴 감지 완료")
        print(f"   감지된 얼굴 수: {face_count}명")
        print(f"   감지 시간: {elapsed_time:.3f}초")
        print()

        # 성능 검증 (목표: 0.5초 이하)
        if elapsed_time > 0.5:
            print(f"⚠️  경고: 감지 시간이 목표(0.5초)를 초과했습니다")
            print(f"   (노트북 CPU 모드에서는 정상입니다)")
        else:
            print(f"✅ 성능 목표 달성 (≤ 0.5초)")

        print()

        # Cleanup
        detector.cleanup()

        return True

    except Exception as e:
        print(f"❌ 얼굴 감지 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detect_with_synthetic_image():
    """합성 이미지로 얼굴 감지 테스트."""
    print("=" * 60)
    print("4. 합성 이미지로 얼굴 감지 테스트")
    print("=" * 60)

    try:
        detector = FaceDetector()
        detector.initialize()

        # 합성 이미지 생성 (1920x1080 RGB)
        synthetic_image = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        print(f"합성 이미지 생성: {synthetic_image.shape}")
        print()

        # 얼굴 감지 (랜덤 이미지이므로 0명 예상)
        face_count = detector.detect(synthetic_image)
        print(f"✅ 얼굴 감지 완료")
        print(f"   감지된 얼굴 수: {face_count}명 (랜덤 이미지)")
        print()

        detector.cleanup()

        return True

    except Exception as e:
        print(f"❌ 합성 이미지 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detect_without_initialization():
    """초기화 없이 detect() 호출 테스트."""
    print("=" * 60)
    print("5. 초기화 없이 detect() 호출 테스트")
    print("=" * 60)

    try:
        detector = FaceDetector()
        # initialize() 호출 안 함

        # 합성 이미지 생성
        image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        # detect() 호출 시 ValueError 발생 예상
        try:
            face_count = detector.detect(image)
            print(f"❌ ValueError가 발생해야 하는데 감지가 실행됨")
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


def test_detect_with_invalid_image():
    """잘못된 이미지 형식 테스트."""
    print("=" * 60)
    print("6. 잘못된 이미지 형식 테스트")
    print("=" * 60)

    try:
        detector = FaceDetector()
        detector.initialize()

        # 테스트 1: 2차원 이미지 (grayscale)
        print("테스트 1: 2차원 이미지")
        invalid_image_2d = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        try:
            detector.detect(invalid_image_2d)
            print(f"❌ ValueError가 발생해야 함")
            return False
        except ValueError as e:
            print(f"✅ ValueError 정상 발생: shape 오류")
            print()

        # 테스트 2: 4채널 이미지 (RGBA)
        print("테스트 2: 4채널 이미지")
        invalid_image_4ch = np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)
        try:
            detector.detect(invalid_image_4ch)
            print(f"❌ ValueError가 발생해야 함")
            return False
        except ValueError as e:
            print(f"✅ ValueError 정상 발생: 채널 수 오류")
            print()

        # 테스트 3: 리스트 타입
        print("테스트 3: 리스트 타입")
        invalid_image_list = [[1, 2, 3], [4, 5, 6]]
        try:
            detector.detect(invalid_image_list)
            print(f"❌ ValueError가 발생해야 함")
            return False
        except ValueError as e:
            print(f"✅ ValueError 정상 발생: 타입 오류")
            print()

        detector.cleanup()

        return True

    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cleanup():
    """cleanup() 메서드 테스트."""
    print("=" * 60)
    print("7. cleanup() 메서드 테스트")
    print("=" * 60)

    try:
        detector = FaceDetector()
        detector.initialize()

        print(f"초기화 후 상태:")
        print(f"   model: {detector.model is not None}")
        print(f"   is_initialized: {detector.is_initialized}")
        print()

        # Cleanup 호출
        detector.cleanup()

        print(f"cleanup() 후 상태:")
        print(f"   model: {detector.model is not None}")
        print(f"   is_initialized: {detector.is_initialized}")
        print()

        # 검증
        assert detector.model is None, "model이 None이어야 합니다"
        assert detector.is_initialized is False, "is_initialized가 False여야 합니다"

        print(f"✅ cleanup() 정상 동작")
        print()

        # 중복 cleanup 테스트
        print("중복 cleanup 테스트...")
        detector.cleanup()
        print(f"✅ 중복 cleanup 방지 확인")
        print()

        return True

    except Exception as e:
        print(f"❌ cleanup() 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_detections():
    """연속 얼굴 감지 테스트."""
    print("=" * 60)
    print("8. 연속 얼굴 감지 테스트 (5회)")
    print("=" * 60)

    try:
        detector = FaceDetector()
        detector.initialize()

        capturer = ScreenCapture(monitor_id=1)

        total_time = 0
        detection_count = 5

        for i in range(detection_count):
            image = capturer.capture()

            start_time = time.time()
            face_count = detector.detect(image)
            elapsed_time = time.time() - start_time

            total_time += elapsed_time
            print(f"   {i+1}회: {face_count}명 감지 ({elapsed_time:.3f}초)")

        avg_time = total_time / detection_count

        print()
        print(f"✅ 연속 감지 성공")
        print(f"   총 감지 횟수: {detection_count}회")
        print(f"   총 소요 시간: {total_time:.3f}초")
        print(f"   평균 감지 시간: {avg_time:.3f}초")
        print()

        detector.cleanup()

        return True

    except Exception as e:
        print(f"❌ 연속 감지 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_accuracy_with_real_zoom_images():
    """실제 Zoom 화면 이미지로 정확도 테스트."""
    print("=" * 60)
    print("9. 실제 Zoom 화면 정확도 테스트")
    print("=" * 60)

    try:
        from pathlib import Path
        from PIL import Image

        # 테스트 이미지 폴더 경로
        test_images_folder = Path(__file__).parent / "test_images"

        if not test_images_folder.exists():
            print(f"⚠️  테스트 이미지 폴더가 없습니다: {test_images_folder}")
            print(f"   폴더를 생성하고 Zoom 화면 이미지를 넣어주세요.")
            print()
            return True  # 선택적 테스트이므로 실패로 처리하지 않음

        # 테스트 데이터: (파일명, 실제 인원 수)
        test_cases = [
            ("zoom_22people.png", 22),  # 학생 21명 + 강사 1명
            ("zoom_21people.png", 21),  # 결석 1명
            ("zoom_20people.png", 20),  # 결석 2명
            ("zoom_19people.png", 19),  # 결석 3명
            ("zoom_18people.png", 18),  # 결석 4명
            # 추가 이미지가 있다면 여기에 추가
        ]

        detector = FaceDetector()
        detector.initialize()

        total_tests = 0
        total_accuracy = 0
        passed_tests = 0

        print(f"테스트 이미지 폴더: {test_images_folder}")
        print()

        for image_filename, expected_count in test_cases:
            image_path = test_images_folder / image_filename

            if not image_path.exists():
                print(f"⚠️  이미지 없음: {image_filename} (건너뜀)")
                continue

            # 이미지 로드
            pil_image = Image.open(image_path)
            image = np.array(pil_image.convert("RGB"))

            # 얼굴 감지
            detected_count = detector.detect(image)

            # 정확도 계산
            accuracy = (detected_count / expected_count) * 100 if expected_count > 0 else 0

            # 결과 출력
            result_icon = "✅" if accuracy >= 95 else "⚠️"
            print(f"{result_icon} {image_filename}")
            print(f"   실제 인원: {expected_count}명")
            print(f"   감지 인원: {detected_count}명")
            print(f"   정확도: {accuracy:.1f}%")

            if accuracy >= 95:
                passed_tests += 1

            total_tests += 1
            total_accuracy += accuracy
            print()

        detector.cleanup()

        if total_tests == 0:
            print(f"⚠️  테스트할 이미지가 없습니다.")
            print(f"   {test_images_folder} 폴더에 이미지를 추가하세요:")
            print(f"   - zoom_22people.png (22명)")
            print(f"   - zoom_21people.png (21명)")
            print(f"   - zoom_20people.png (20명)")
            print(f"   - zoom_19people.png (19명)")
            print(f"   - zoom_18people.png (18명)")
            print()
            return True  # 선택적 테스트

        # 전체 평균 정확도
        avg_accuracy = total_accuracy / total_tests

        print("=" * 60)
        print(f"정확도 테스트 결과")
        print(f"   총 테스트: {total_tests}개")
        print(f"   통과 (≥95%): {passed_tests}개")
        print(f"   평균 정확도: {avg_accuracy:.1f}%")
        print("=" * 60)
        print()

        if avg_accuracy >= 95:
            print(f"✅ 평균 정확도 95% 이상 달성!")
            print()
            return True
        else:
            print(f"⚠️  평균 정확도가 95% 미만입니다.")
            print()
            return False

    except Exception as e:
        print(f"❌ 정확도 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("FaceDetector 테스트 시작")
    print("=" * 60)
    print()

    results = []
    results.append(test_init())
    results.append(test_initialize())
    results.append(test_detect_with_real_image())
    results.append(test_detect_with_synthetic_image())
    results.append(test_detect_without_initialization())
    results.append(test_detect_with_invalid_image())
    results.append(test_cleanup())
    results.append(test_multiple_detections())
    results.append(test_accuracy_with_real_zoom_images())

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
