"""
커스텀 예외 클래스 모듈.

출결 관리 자동 캡처 프로그램에서 사용하는 모든 커스텀 예외를 정의합니다.
표준 예외(RuntimeError, ValueError 등) 대신 명확한 타입의 예외를 사용하여
에러 타입 구분 및 디버깅 용이성을 향상시킵니다.
"""


class CaptureException(Exception):
    """
    모든 커스텀 예외의 기본 클래스.

    프로그램에서 발생하는 모든 커스텀 예외는 이 클래스를 상속합니다.
    표준 Exception을 상속하여 기본 예외 처리 메커니즘과 호환됩니다.

    Example:
        >>> try:
        ...     raise CaptureException("기본 에러")
        ... except CaptureException as e:
        ...     print(f"에러 발생: {e}")
        에러 발생: 기본 에러
    """
    pass


# ==================== 화면 캡처 예외 ====================

class ScreenCaptureError(CaptureException):
    """
    화면 캡처 실패 시 발생하는 예외.

    mss 라이브러리를 사용한 화면 캡처 중 오류가 발생했을 때 raise됩니다.
    모니터 연결 문제, mss 인스턴스 생성 실패 등이 원인일 수 있습니다.

    Raises:
        ScreenCaptureError: 화면 캡처 실패 시

    Example:
        >>> try:
        ...     screenshot = capturer.capture()
        ... except ScreenCaptureError as e:
        ...     logger.error(f"화면 캡처 실패: {e}")
    """
    pass


class InvalidMonitorError(ScreenCaptureError):
    """
    유효하지 않은 모니터 ID로 접근 시 발생하는 예외.

    선택한 모니터 ID가 연결된 모니터 개수를 초과하거나,
    프로그램 실행 중 모니터 연결이 해제된 경우 발생합니다.

    사용자 알림 필요: 모니터 재선택 안내

    Raises:
        InvalidMonitorError: 유효하지 않은 모니터 ID 접근 시

    Example:
        >>> capturer = ScreenCapture(monitor_id=5)  # 모니터 2개만 연결됨
        >>> capturer.capture()
        InvalidMonitorError: 모니터 ID 5를 찾을 수 없습니다.
    """
    pass


# ==================== 얼굴 감지 예외 ====================

class FaceDetectionError(CaptureException):
    """
    얼굴 감지 실패 시 발생하는 예외.

    InsightFace를 사용한 얼굴 감지 중 오류가 발생했을 때 raise됩니다.
    이미지 처리 실패, GPU 메모리 부족 등이 원인일 수 있습니다.

    Raises:
        FaceDetectionError: 얼굴 감지 실패 시

    Example:
        >>> try:
        ...     face_count = detector.detect(image)
        ... except FaceDetectionError as e:
        ...     logger.error(f"얼굴 감지 실패: {e}")
    """
    pass


class ModelLoadError(FaceDetectionError):
    """
    InsightFace 모델 로드 실패 시 발생하는 예외.

    InsightFace 라이브러리 미설치, 모델 파일 손상,
    GPU/CPU 초기화 실패 등이 원인일 수 있습니다.

    사용자 알림 필요: InsightFace 설치 확인 안내

    Raises:
        ModelLoadError: 모델 로드 실패 시

    Example:
        >>> try:
        ...     detector.initialize()
        ... except ModelLoadError as e:
        ...     print("InsightFace 모델을 로드할 수 없습니다.")
    """
    pass


class InvalidImageError(FaceDetectionError):
    """
    이미지 형식 오류 시 발생하는 예외.

    이미지가 None이거나, 빈 배열이거나, 잘못된 형식(RGB가 아닌 경우)일 때
    발생합니다.

    Raises:
        InvalidImageError: 이미지 유효성 검사 실패 시

    Example:
        >>> detector.detect(None)
        InvalidImageError: 이미지가 None입니다.

        >>> detector.detect(np.array([]))
        InvalidImageError: 이미지가 비어있습니다.
    """
    pass


# ==================== 파일 저장 예외 ====================

class FileSaveError(CaptureException):
    """
    파일 저장 실패 시 발생하는 예외.

    이미지 파일을 디스크에 저장하는 중 오류가 발생했을 때 raise됩니다.
    디스크 공간 부족, 권한 문제, 경로 오류 등이 원인일 수 있습니다.

    Raises:
        FileSaveError: 파일 저장 실패 시

    Example:
        >>> try:
        ...     file_manager.save_image(image, period=1)
        ... except FileSaveError as e:
        ...     logger.error(f"파일 저장 실패: {e}")
    """
    pass


class InsufficientStorageError(FileSaveError):
    """
    디스크 공간 부족 시 발생하는 예외.

    저장 경로의 디스크 공간이 부족하여 파일을 저장할 수 없을 때
    발생합니다.

    사용자 알림 필요: 디스크 공간 확보 안내

    Raises:
        InsufficientStorageError: 디스크 공간 부족 시

    Example:
        >>> try:
        ...     file_manager.save_image(large_image, period=1)
        ... except InsufficientStorageError:
        ...     print("디스크 공간이 부족합니다. 파일을 삭제해주세요.")
    """
    pass


class FilePermissionError(FileSaveError):
    """
    파일 저장 권한 없음 시 발생하는 예외.

    저장 경로에 대한 쓰기 권한이 없거나, 폴더 생성 권한이 없을 때
    발생합니다.

    사용자 알림 필요: 저장 경로 변경 안내

    Raises:
        FilePermissionError: 파일 저장 권한 없음 시

    Example:
        >>> try:
        ...     file_manager.save_image(image, period=1)
        ... except FilePermissionError:
        ...     print("저장 경로에 대한 권한이 없습니다.")
    """
    pass


# ==================== 스케줄러 예외 ====================

class SchedulerError(CaptureException):
    """
    스케줄러 오류 시 발생하는 예외.

    스케줄러 실행 중 오류가 발생했을 때 raise됩니다.
    스케줄러 중복 실행, 콜백 함수 오류 등이 원인일 수 있습니다.

    Raises:
        SchedulerError: 스케줄러 오류 시

    Example:
        >>> try:
        ...     scheduler.start()
        ... except SchedulerError as e:
        ...     logger.error(f"스케줄러 오류: {e}")
    """
    pass


class InvalidScheduleError(SchedulerError):
    """
    잘못된 스케줄 형식 시 발생하는 예외.

    스케줄 시간 형식이 잘못되었거나, 시작 시간이 종료 시간보다
    늦은 경우 등 스케줄 검증 실패 시 발생합니다.

    Raises:
        InvalidScheduleError: 잘못된 스케줄 형식 시

    Example:
        >>> scheduler.add_schedule(1, "25:00", "26:00", callback)
        InvalidScheduleError: 잘못된 시간 형식입니다.

        >>> scheduler.add_schedule(1, "10:00", "09:00", callback)
        InvalidScheduleError: 시작 시간이 종료 시간보다 늦습니다.
    """
    pass
