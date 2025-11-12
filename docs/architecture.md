# 기술 설계서 (Technical Architecture)

출결 관리 자동 캡처 프로그램의 기술적 구조와 설계를 정의합니다.

---

## 1. 시스템 아키텍처

### 1.1 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                      Main Application                   │
│                       (main.py)                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│   GUI    │  │ Features │  │  Utils   │
│ (tkinter)│  │  (Core)  │  │          │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     │             │             │
     └─────────────┼─────────────┘
                   │
                   ▼
           ┌───────────────┐
           │   External    │
           │   Libraries   │
           ├───────────────┤
           │ InsightFace   │
           │ mss           │
           │ Pillow        │
           └───────────────┘
```

### 1.2 아키텍처 패턴

**MVC 변형 패턴 사용:**
- **View**: GUI 레이어 (`gui/`)
- **Controller**: Features 레이어 (`features/`)
- **Model**: 데이터 구조 및 설정 (`utils/config.py`)

**특징:**
- 레이어 간 느슨한 결합
- 각 모듈은 독립적으로 테스트 가능
- 단방향 데이터 흐름

---

## 2. 모듈 구조

### 2.1 features/ (핵심 비즈니스 로직)

```
features/
├─ capture.py          # 화면 캡처
├─ face_detection.py   # 얼굴 감지
├─ file_manager.py     # 파일 저장
├─ logger.py           # CSV 로깅
└─ scheduler.py        # 스케줄링
```

**역할:**
- 핵심 기능 구현
- GUI와 독립적
- 재사용 가능한 비즈니스 로직

### 2.2 gui/ (사용자 인터페이스)

```
gui/
├─ main_window.py      # 메인 윈도우
└─ dialogs.py          # 다이얼로그
```

**역할:**
- 사용자 인터페이스 제공
- Features 레이어 호출
- 상태 표시 및 사용자 입력 처리

### 2.3 utils/ (유틸리티)

```
utils/
├─ config.py           # 설정 관리
└─ monitor.py          # 모니터 감지
```

**역할:**
- 공통 유틸리티 함수
- 설정 파일 관리
- 시스템 정보 조회

---

## 3. 주요 클래스 설계

### 3.1 ScreenCapture (features/capture.py)

**목적:** 듀얼 모니터 환경에서 특정 모니터의 화면 캡처

```python
class ScreenCapture:
    """
    화면 캡처 클래스.
    
    Attributes:
        monitor_id (int): 캡처할 모니터 ID
        mss_instance: mss 스크린샷 인스턴스
    """
    
    def __init__(self, monitor_id: int = 1):
        """
        Args:
            monitor_id: 캡처할 모니터 ID (1=주, 2=보조)
        """
        pass
    
    def capture(self) -> np.ndarray:
        """
        현재 모니터 화면을 캡처합니다.
        
        Returns:
            np.ndarray: 캡처된 이미지 (RGB)
        
        Raises:
            RuntimeError: 캡처 실패 시
        """
        pass
    
    def get_monitor_info(self) -> dict:
        """
        모니터 정보를 반환합니다.

        듀얼 모니터 환경에서 캡처 영역 계산 및 
        디버깅 로그 기록 시 사용됩니다.
        
        Returns:
            dict: {width, height, left, top}
        """
        pass
```

**주요 메서드:**
- `capture()`: 화면 캡처 실행
- `get_monitor_info()`: 모니터 해상도 및 위치 정보

**의존성:**
- `mss`: 스크린샷 라이브러리
- `numpy`: 이미지 데이터 처리

---

### 3.2 FaceDetector (features/face_detection.py)

**목적:** InsightFace를 사용한 얼굴 감지

```python
class FaceDetector:
    """
    InsightFace 기반 얼굴 감지 클래스.
    
    Attributes:
        gpu_id (int): GPU ID (-1=CPU, 0=GPU)
        model: InsightFace 모델 인스턴스
        is_initialized (bool): 초기화 여부
    """
    
    def __init__(self, gpu_id: int = 0):
        """
        Args:
            gpu_id: 사용할 GPU ID
        """
        pass
    
    def initialize(self) -> None:
        """
        InsightFace 모델을 로드합니다.
        
        Raises:
            RuntimeError: GPU 사용 불가 시 CPU로 전환
        """
        pass
    
    def detect(self, image: np.ndarray) -> int:
        """
        이미지에서 얼굴을 감지합니다.
        
        Args:
            image: 입력 이미지 (RGB)
        
        Returns:
            int: 감지된 얼굴 개수
        
        Raises:
            ValueError: 이미지가 유효하지 않을 때
        """
        pass
    
    def cleanup(self) -> None:
        """GPU 메모리를 해제합니다."""
        pass
```

**주요 메서드:**
- `initialize()`: 모델 로드 (무거운 작업)
- `detect()`: 얼굴 감지 및 개수 반환
- `cleanup()`: GPU 메모리 해제

**의존성:**
- `insightface`: 얼굴 감지 라이브러리
- `onnxruntime-gpu`: GPU 가속

---

### 3.3 FileManager (features/file_manager.py)

**목적:** 캡처 이미지 파일 저장 관리

```python
class FileManager:
    """
    파일 저장 관리 클래스.
    
    Attributes:
        base_path (Path): 기본 저장 경로
        current_date (str): 현재 날짜 (YYMMDD)
    """
    
    def __init__(self, base_path: str = "C:/IBM 비대면"):
        """
        Args:
            base_path: 기본 저장 경로
        """
        pass
    
    def save_image(
        self,
        image: np.ndarray,
        period: int,
        is_within_window: bool
    ) -> str:
        """
        이미지를 저장합니다.

        Args:
            image: 저장할 이미지
            period: 교시 (1~8) 또는 0(퇴실)
            is_within_window: 캡처 시간대 내 여부
                - True: 시간대 내 → 덮어쓰기
                - False: 시간대 종료 후 → _수정.png

        Returns:
            str: 저장된 파일 경로

        Example:
            >>> fm = FileManager()
            >>> path = fm.save_image(img, 1, True)
            "C:/IBM 비대면/251020/251020_1교시.png"
            >>> path = fm.save_image(img, 1, False)
            "C:/IBM 비대면/251020/251020_1교시_수정.png"
        """
        pass
    
    def ensure_folder_exists(self) -> None:
        """날짜 폴더를 생성합니다."""
        pass
    
    def get_file_path(self, period: int, is_within_window: bool) -> Path:
        """
        파일 경로를 생성합니다.

        Args:
            period: 교시 번호
            is_within_window: 시간대 내 여부

        Returns:
            Path: 파일 경로
        """
        pass
```

**주요 메서드:**
- `save_image()`: 이미지 저장
- `ensure_folder_exists()`: 폴더 생성
- `get_file_path()`: 파일 경로 생성

**파일명 규칙:**
- 일반: `YYMMDD_N교시.png`
- 수정: `YYMMDD_N교시_수정.png`
- 퇴실: `YYMMDD_퇴실.png`

---

### 3.4 CSVLogger (features/logger.py)

**목적:** CSV 형식으로 로그 기록

```python
class CSVLogger:
    """
    CSV 로그 기록 클래스.
    
    Attributes:
        log_path (Path): 로그 파일 경로
    """
    
    def __init__(self, base_path: str = "C:/IBM 비대면"):
        """
        Args:
            base_path: 기본 저장 경로
        """
        pass
    
    def log_event(
        self,
        period: str,
        status: str,
        detected_count: int,
        threshold_count: int,
        filename: str = "",
        note: str = ""
    ) -> None:
        """
        이벤트를 로그에 기록합니다.
        
        Args:
            period: 교시 (1교시, 2교시, 퇴실 등)
            status: 상태 (캡처 시작, 감지 완료, 캡처 성공 등)
            detected_count: 감지된 인원
            threshold_count: 기준 인원
            filename: 저장된 파일명
            note: 비고
        """
        pass
    
    def _ensure_log_file(self) -> None:
        """
        로그 파일이 없으면 헤더와 함께 생성합니다.

        UTF-8-BOM 인코딩 사용 (Excel 호환).
        """
        pass
```

**주요 메서드:**
- `log_event()`: 이벤트 기록
- `_ensure_log_file()`: 로그 파일 초기화

**CSV 구조:**
```csv
날짜,시간,항목,상태,감지인원,기준인원,파일명,비고
```

---

### 3.5 CaptureScheduler (features/scheduler.py)

**목적:** 교시별 캡처 스케줄 관리

```python
class CaptureScheduler:
    """
    캡처 스케줄링 클래스.
    
    Attributes:
        schedules (List[Schedule]): 스케줄 목록
        is_running (bool): 실행 중 여부
    """
    
    def __init__(self):
        """스케줄 초기화"""
        pass
    
    def add_schedule(
        self,
        period: int,
        start_time: str,
        end_time: str,
        callback: Callable
    ) -> None:
        """
        스케줄을 추가합니다.
        
        Args:
            period: 교시 번호
            start_time: 시작 시간 (HH:MM)
            end_time: 종료 시간 (HH:MM)
            callback: 캡처 시도 시 호출할 함수
        """
        pass
    
    def start(self) -> None:
        """스케줄러를 시작합니다."""
        pass
    
    def stop(self) -> None:
        """스케줄러를 중지합니다."""
        pass
    
    def skip_period(self, period: int) -> None:
        """특정 교시를 건너뜁니다."""
        pass

    def mark_completed(self, period: int) -> None:
        """교시 완료 처리 (캡처 성공 시 호출)."""
        pass

    def reset_period(self, period: int) -> None:
        """재시도용 초기화 (재시도 버튼 클릭 시 호출)."""
        pass

    def is_in_capture_window(self, period: int) -> bool:
        """
        현재 시간이 캡처 시간대인지 확인합니다.
        
        Args:
            period: 교시 번호
        
        Returns:
            bool: 캡처 시간대 여부
        """
        pass
```

**주요 메서드:**
- `add_schedule()`: 스케줄 등록
- `start()`: 스케줄러 시작
- `stop()`: 스케줄러 중지
- `skip_period()`: 건너뛰기
- `mark_completed()`: 교시 완료 처리
- `reset_period()`: 재시도용 초기화
- `is_in_capture_window()`: 시간대 확인

**스케줄 구조:**
```python
Schedule = {
    'period': 1,
    'start_time': '09:30',
    'end_time': '09:45',
    'callback': capture_function,
    'is_skipped': False,
    'is_completed': False
}
```

---

### 3.6 MainWindow (gui/main_window.py)

**목적:** 메인 GUI 윈도우

```python
class MainWindow:
    """
    메인 윈도우 클래스.
    
    Attributes:
        root (tk.Tk): tkinter 루트 윈도우
        capture: ScreenCapture 인스턴스
        detector: FaceDetector 인스턴스
        file_manager: FileManager 인스턴스
        logger: CSVLogger 인스턴스
        scheduler: CaptureScheduler 인스턴스
    """
    
    def __init__(self):
        """GUI 초기화"""
        pass
    
    def setup_ui(self) -> None:
        """UI 구성요소를 배치합니다."""
        pass
    
    def update_time(self) -> None:
        """현재 시간을 업데이트합니다 (1초마다)."""
        pass
    
    def update_period_status(self, period: int, status: str) -> None:
        """
        교시 상태를 업데이트합니다.
        
        Args:
            period: 교시 번호
            status: 상태 (대기중, 감지중, 완료 등)
        """
        pass
    
    def on_skip_button(self, period: int) -> None:
        """건너뛰기 버튼 클릭 핸들러"""
        pass
    
    def on_retry_button(self, period: int) -> None:
        """재시도 버튼 클릭 핸들러"""
        pass

    def show_alert(self, title: str, message: str) -> None:
        """알림창을 표시합니다."""
        pass

    def cleanup(self) -> None:
        """
        프로그램 종료 시 리소스 정리.

        - Scheduler 중지
        - FaceDetector GPU 메모리 해제
        - 기타 리소스 정리

        Note:
            윈도우 종료 시 자동 호출됩니다.
        """
        pass
```

**주요 메서드:**
- `setup_ui()`: UI 초기화
- `update_time()`: 시간 업데이트
- `update_period_status()`: 상태 업데이트
- `on_skip_button()`: 건너뛰기 처리
- `on_retry_button()`: 재시도 처리
- `show_alert()`: 알림창 표시
- `cleanup()`: 리소스 정리 (종료 시)

---

### 3.7 InitDialog (gui/dialogs.py)

**목적:** 초기 설정 다이얼로그

```python
class InitDialog:
    """
    초기 설정 다이얼로그.
    
    Attributes:
        dialog (tk.Toplevel): 다이얼로그 윈도우
        result (dict): 사용자 입력 결과
    """
    
    def __init__(self, parent):
        """
        Args:
            parent: 부모 윈도우
        """
        pass
    
    def show(self) -> dict:
        """
        다이얼로그를 표시하고 결과를 반환합니다.
        
        Returns:
            dict: {
                'monitor_id': int,
                'save_path': str,
                'mode': str,  # 'exact' or 'flexible'
                'student_count': int
            }
        """
        pass
    
    def on_ok(self) -> None:
        """확인 버튼 핸들러"""
        pass

    def on_cancel(self) -> None:
        """취소 버튼 핸들러"""
        pass

    def validate_input(self) -> bool:
        """
        입력값을 검증합니다.

        Returns:
            bool: 유효성 여부

        Validation:
            - 학생 수: 1~100명
            - 저장 경로: 폴더 존재 여부
        """
        pass
```

---

## 4. 데이터 흐름

### 4.1 캡처 프로세스

```
1. Scheduler (시간 도달)
   ↓
2. MainWindow._on_capture_trigger(period)
   ↓
3. ScreenCapture.capture()
   ↓ (image)
4. FaceDetector.detect(image)
   ↓ (face_count)
5. 조건 확인 (face_count >= threshold)
   ↓ YES
6. FileManager.save_image(image)
   ↓
7. CSVLogger.log_event()
   ↓
8. MainWindow.update_period_status()
   ↓
9. MainWindow.show_alert() (성공)
```

### 4.2 재시도 프로세스

```
1. MainWindow.on_retry_button(period)
   ↓
2. Scheduler.reset_period(period)
   ↓
3. Scheduler.is_in_capture_window(period) 확인
   ↓ 시간대 내
4. 즉시 캡처 프로세스 실행 (덮어쓰기)
   ↓ 시간대 종료 후
5. 즉시 캡처 프로세스 실행 (_수정.png)
```

---

## 5. 설정 관리

### 5.1 Config 클래스 (utils/config.py)

```python
class Config:
    """
    설정 관리 클래스.
    
    Attributes:
        config_path (Path): 설정 파일 경로
        data (dict): 설정 데이터
    """
    
    def __init__(self, config_path: str = "config.json"):
        pass
    
    def load(self) -> dict:
        """설정을 로드합니다."""
        pass
    
    def save(self, data: dict) -> None:
        """설정을 저장합니다."""
        pass
    
    def get(self, key: str, default=None):
        """설정 값을 가져옵니다."""
        pass
    
    def set(self, key: str, value) -> None:
        """설정 값을 설정합니다."""
        pass
```

### 5.2 설정 파일 구조 (config.json)

```json
{
  "monitor_id": 2,
  "save_path": "C:/IBM 비대면",
  "mode": "flexible",
  "student_count": 21,
  "threshold_ratio": 0.9,
  "last_updated": "2025-10-21T10:00:00"
}
```

---

## 6. 에러 처리 전략

### 6.1 예외 계층

```
CaptureException (기본)
├─ ScreenCaptureError (화면 캡처 실패)
├─ FaceDetectionError (얼굴 감지 실패)
│  ├─ GPUNotAvailableError (GPU 사용 불가)
│  └─ ModelLoadError (모델 로드 실패)
├─ FileSaveError (파일 저장 실패)
└─ SchedulerError (스케줄러 오류)
```

### 6.2 에러 처리 패턴

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"작업 실패: {e}")
    # 복구 시도
    fallback_operation()
except Exception as e:
    logger.critical(f"예상치 못한 오류: {e}", exc_info=True)
    # 사용자에게 알림
    show_error_dialog(str(e))
```

---

## 7. 성능 고려사항

### 7.1 메모리 관리

**GPU 메모리:**
- InsightFace 모델: 약 500MB
- 처리 후 명시적 해제 (`cleanup()`)

**이미지 메모리:**
- 듀얼 모니터 스크린샷: 약 10~20MB
- 처리 후 즉시 삭제 (`del image`)

### 7.2 성능 목표

| 항목 | 목표 |
|------|------|
| 화면 캡처 | 0.5초 이하 |
| 얼굴 감지 (GPU) | 0.5초 이하 |
| 파일 저장 | 0.5초 이하 |
| **총 처리 시간** | **2초 이하** |

### 7.3 최적화 전략

1. **모델 재사용**: FaceDetector 인스턴스 재사용
2. **비동기 처리**: 파일 저장을 별도 스레드로
3. **메모리 해제**: 큰 객체는 즉시 삭제

---

## 8. 의존성 관리

### 8.1 핵심 라이브러리

```python
# requirements.txt
insightface==0.7.3
onnxruntime-gpu==1.16.3
mss==9.0.1
Pillow==10.1.0
numpy==1.24.3
```

### 8.2 의존성 그래프

```
main.py
├─ gui/
│  ├─ tkinter (내장)
│  └─ features/*
├─ features/
│  ├─ insightface
│  ├─ mss
│  ├─ Pillow
│  └─ numpy
└─ utils/
   └─ (내장 라이브러리만)
```

---

## 9. 확장 가능성

### 9.1 향후 추가 가능 기능

**시스템 트레이:**
```python
# gui/tray_icon.py (미래)
class TrayIcon:
    def minimize_to_tray(self): pass
    def restore_from_tray(self): pass
```

**다중 감지 모델:**
```python
# features/face_detection.py
class FaceDetector:
    def __init__(self, model_type='insightface'):
        # 'insightface', 'mtcnn', 'retinaface' 지원
        pass
```

**클라우드 업로드:**
```python
# features/cloud_uploader.py (미래)
class CloudUploader:
    def upload_to_drive(self, file_path): pass
```

---

## 10. 보안 고려사항

### 10.1 데이터 보호

- 캡처 이미지: 로컬 저장만, 외부 전송 없음
- 로그 파일: 개인 식별 정보 최소화
- 설정 파일: 민감 정보 암호화 고려 (미래)

### 10.2 접근 제어

- 저장 폴더: Windows 파일 권한 활용
- 프로그램 실행: 관리자 권한 불필요

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-10-23