"""
스케줄러 기능 테스트 스크립트.

CaptureScheduler 클래스가 정상 작동하는지 확인합니다.
"""

# 표준 라이브러리
import sys
import time
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 내부 모듈
from features.scheduler import CaptureScheduler


def test_init():
    """CaptureScheduler 초기화 테스트."""
    print("=" * 60)
    print("1. CaptureScheduler 초기화 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()
        print(f"✅ 초기화 성공")
        print(f"   schedules: {scheduler.schedules}")
        print(f"   is_running: {scheduler.is_running}")
        print()
        return True

    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_schedule():
    """스케줄 추가 테스트."""
    print("=" * 60)
    print("2. 스케줄 추가 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        # 정상적인 스케줄 추가
        def dummy_callback(period):
            print(f"Callback called: period={period}")

        scheduler.add_schedule(1, "09:30", "09:45", dummy_callback)
        print(f"✅ 1교시 스케줄 추가 성공")
        print(f"   period: {scheduler.schedules[0]['period']}")
        print(f"   start_time: {scheduler.schedules[0]['start_time']}")
        print(f"   end_time: {scheduler.schedules[0]['end_time']}")
        print(f"   is_skipped: {scheduler.schedules[0]['is_skipped']}")
        print(f"   is_completed: {scheduler.schedules[0]['is_completed']}")
        print()

        # 잘못된 시간 형식 테스트
        try:
            scheduler.add_schedule(2, "25:00", "26:00", dummy_callback)
            print(f"❌ 잘못된 시간 형식 검증 실패")
            return False
        except ValueError as e:
            print(f"✅ 잘못된 시간 형식 검증 성공: {e}")
            print()

        # 시작 시간 >= 종료 시간 테스트
        try:
            scheduler.add_schedule(3, "10:30", "10:30", dummy_callback)
            print(f"❌ 시간 범위 검증 실패")
            return False
        except ValueError as e:
            print(f"✅ 시간 범위 검증 성공: {e}")
            print()

        return True

    except Exception as e:
        print(f"❌ 스케줄 추가 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_is_in_capture_window():
    """캡처 시간대 확인 테스트."""
    print("=" * 60)
    print("3. 캡처 시간대 확인 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        def dummy_callback(period):
            pass

        # 현재 시간 기준으로 스케줄 추가
        now = datetime.now()
        current_hour = now.strftime("%H")
        current_min = now.strftime("%M")

        # 현재 시간 - 1분 ~ 현재 시간 + 1분 범위
        start_min = (int(current_min) - 1) % 60
        end_min = (int(current_min) + 1) % 60
        start_time = f"{current_hour}:{start_min:02d}"
        end_time = f"{current_hour}:{end_min:02d}"

        scheduler.add_schedule(1, start_time, end_time, dummy_callback)

        # 시간대 확인
        is_in_window = scheduler.is_in_capture_window(1)
        print(f"현재 시간: {current_hour}:{current_min}")
        print(f"캡처 시간대: {start_time} ~ {end_time}")
        print(f"시간대 내 여부: {is_in_window}")
        print()

        # 존재하지 않는 교시 테스트
        is_in_window_invalid = scheduler.is_in_capture_window(99)
        print(f"✅ 존재하지 않는 교시 처리: {is_in_window_invalid}")
        print()

        return True

    except Exception as e:
        print(f"❌ 시간대 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skip_period():
    """건너뛰기 기능 테스트."""
    print("=" * 60)
    print("4. 건너뛰기 기능 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        def dummy_callback(period):
            pass

        scheduler.add_schedule(1, "09:30", "09:45", dummy_callback)

        # 건너뛰기 전
        print(f"건너뛰기 전: is_skipped={scheduler.schedules[0]['is_skipped']}")

        # 건너뛰기
        scheduler.skip_period(1)
        print(f"건너뛰기 후: is_skipped={scheduler.schedules[0]['is_skipped']}")
        print()

        if scheduler.schedules[0]['is_skipped']:
            print(f"✅ 건너뛰기 기능 성공")
        else:
            print(f"❌ 건너뛰기 기능 실패")
            return False

        # 존재하지 않는 교시 테스트
        scheduler.skip_period(99)
        print(f"✅ 존재하지 않는 교시 처리 성공")
        print()

        return True

    except Exception as e:
        print(f"❌ 건너뛰기 기능 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mark_completed():
    """완료 처리 기능 테스트."""
    print("=" * 60)
    print("5. 완료 처리 기능 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        def dummy_callback(period):
            pass

        scheduler.add_schedule(1, "09:30", "09:45", dummy_callback)

        # 완료 처리 전
        print(f"완료 처리 전: is_completed={scheduler.schedules[0]['is_completed']}")

        # 완료 처리
        scheduler.mark_completed(1)
        print(f"완료 처리 후: is_completed={scheduler.schedules[0]['is_completed']}")
        print()

        if scheduler.schedules[0]['is_completed']:
            print(f"✅ 완료 처리 기능 성공")
        else:
            print(f"❌ 완료 처리 기능 실패")
            return False

        # 존재하지 않는 교시 테스트
        scheduler.mark_completed(99)
        print(f"✅ 존재하지 않는 교시 처리 성공")
        print()

        return True

    except Exception as e:
        print(f"❌ 완료 처리 기능 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reset_period():
    """재시도 초기화 기능 테스트."""
    print("=" * 60)
    print("6. 재시도 초기화 기능 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        def dummy_callback(period):
            pass

        scheduler.add_schedule(1, "09:30", "09:45", dummy_callback)

        # 완료 및 건너뛰기 설정
        scheduler.mark_completed(1)
        scheduler.skip_period(1)
        print(f"초기화 전: is_completed={scheduler.schedules[0]['is_completed']}, "
              f"is_skipped={scheduler.schedules[0]['is_skipped']}")

        # 초기화
        scheduler.reset_period(1)
        print(f"초기화 후: is_completed={scheduler.schedules[0]['is_completed']}, "
              f"is_skipped={scheduler.schedules[0]['is_skipped']}")
        print()

        if not scheduler.schedules[0]['is_completed'] and not scheduler.schedules[0]['is_skipped']:
            print(f"✅ 재시도 초기화 기능 성공")
        else:
            print(f"❌ 재시도 초기화 기능 실패")
            return False

        # 존재하지 않는 교시 테스트
        scheduler.reset_period(99)
        print(f"✅ 존재하지 않는 교시 처리 성공")
        print()

        return True

    except Exception as e:
        print(f"❌ 재시도 초기화 기능 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_interval():
    """10초 간격 재시도 로직 테스트."""
    print("=" * 60)
    print("7. 10초 간격 재시도 로직 테스트")
    print("=" * 60)

    try:
        scheduler = CaptureScheduler()

        # callback 호출 기록
        call_times = []

        def test_callback(period):
            call_times.append(time.time())
            print(f"   Callback 호출: period={period}, "
                  f"시간={datetime.now().strftime('%H:%M:%S')}")

        # 현재 시간 기준으로 30초 범위 스케줄 추가
        now = datetime.now()
        current_hour = now.strftime("%H")
        current_min = now.strftime("%M")

        start_time = f"{current_hour}:{current_min}"
        # 30초 후 종료
        end_min = (int(current_min) + 1) % 60
        end_time = f"{current_hour}:{end_min:02d}"

        scheduler.add_schedule(1, start_time, end_time, test_callback)

        print(f"테스트 시작: {datetime.now().strftime('%H:%M:%S')}")
        print(f"캡처 시간대: {start_time} ~ {end_time}")
        print(f"예상: 10초 간격으로 callback 호출")
        print()

        # 25초 동안 수동으로 체크 (최소 2회 호출 예상)
        scheduler.is_running = True
        for i in range(25):
            # _check_schedules 로직 수동 실행
            current_timestamp = int(time.time())
            schedule = scheduler.schedules[0]

            if scheduler.is_in_capture_window(1):
                last_attempt = scheduler._last_attempt.get(1, 0)
                time_diff = current_timestamp - last_attempt

                if time_diff >= 10:  # RETRY_INTERVAL
                    scheduler._last_attempt[1] = current_timestamp
                    schedule["callback"](1)

            time.sleep(1)

        scheduler.is_running = False
        print()

        # 호출 횟수 확인
        call_count = len(call_times)
        print(f"총 callback 호출 횟수: {call_count}")

        if call_count >= 2:
            # 호출 간격 확인
            for i in range(1, call_count):
                interval = call_times[i] - call_times[i-1]
                print(f"   {i}번째 간격: {interval:.1f}초")

            print()
            print(f"✅ 10초 간격 재시도 로직 성공 (최소 2회 호출)")
            return True
        else:
            print(f"❌ 10초 간격 재시도 로직 실패 (호출 {call_count}회)")
            return False

    except Exception as e:
        print(f"❌ 10초 간격 재시도 로직 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 테스트 실행."""
    print("\n" + "=" * 60)
    print("CaptureScheduler 테스트 시작")
    print("=" * 60 + "\n")

    results = []

    # 테스트 실행
    results.append(("초기화", test_init()))
    results.append(("스케줄 추가", test_add_schedule()))
    results.append(("시간대 확인", test_is_in_capture_window()))
    results.append(("건너뛰기", test_skip_period()))
    results.append(("완료 처리", test_mark_completed()))
    results.append(("재시도 초기화", test_reset_period()))
    results.append(("10초 간격 재시도", test_retry_interval()))

    # 결과 출력
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    success_count = 0
    for name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{name}: {status}")
        if result:
            success_count += 1

    print()
    print(f"총 {len(results)}개 테스트 중 {success_count}개 성공")
    print("=" * 60 + "\n")

    return success_count == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
