# Task 체크리스트 (Tasks Checklist)

출결 관리 자동 캡처 프로그램 개발 Task 목록입니다.

---

## ⚠️ 개발 시 필수 규칙

### Phase 시작 전
1. 이전 Phase의 주요 기능이 실제로 동작하는지 확인
2. `docs/rules.md` 다시 읽기 (코딩 규칙 상기)
3. Git 브랜치 생성 (`feature/xxx`)

### Task 완료 후
1. 실제로 동작하는지 테스트 (수동 실행)
2. rules.md 기준으로 코드 리뷰
   - 네이밍 규칙 (snake_case, PascalCase)
   - Docstring 작성
   - Type Hints 추가
   - 함수 길이 50줄 이하
   - 에러 처리 (try-except)
3. Git 커밋 (`feat:`, `fix:`, `docs:` 등)

---

## 📋 Phase 1: 핵심 기능 (Core Features)

### 1.1 프로젝트 초기 설정
- [x] 프로젝트 폴더 구조 생성 (`features/`, `gui/`, `utils/`)
- [x] `requirements.txt` 작성
- [x] Git 저장소 초기화 및 `.gitignore` 설정
- [x] 가상환경 생성 (Python 3.10.11)
- [x] 기본 라이브러리 설치 (InsightFace, mss, Pillow 등)

### 1.2 초기 설정 GUI
- [x] `gui/dialogs.py` 생성
- [x] `InitDialog` 클래스 구현
- [x] 모니터 선택 UI (드롭다운)
- [x] 저장 경로 선택 UI (폴더 선택 버튼)
- [x] 캡처 모드 선택 UI (정확/유연)
- [x] 출석 학생 수 입력 UI (텍스트 + ▲▼ 버튼)
- [x] 확인/취소 버튼
- [x] `validate_input()`: 입력값 검증 (학생 수 1~100명)
- [x] `show()`: 설정 결과 반환 (dict)

### 1.3 메인 GUI
- [x] `gui/main_window.py` 생성
- [x] `MainWindow` 클래스 기본 구조
- [x] `__init__()`: tkinter 윈도우 생성
- [x] `setup_ui()`: UI 배치
- [x] 상단 정보 영역 UI
- [x] 날짜 표시 (실시간)
- [x] `update_time()`: 시간 표시 (1초 업데이트)
- [x] 현재 상태 표시 (다음 교시까지 남은 시간)
- [x] 캡처 모니터 표시 및 [변경] 버튼
- [x] 인원 관리 영역 UI
- [x] 캡처 모드 드롭다운
- [x] 출석 학생 수 입력 (텍스트 + ▲▼)
- [x] 기준 인원 표시 (자동 계산)
- [x] 교시별 상태 영역 UI
- [x] 1~8교시 + 퇴실 상태 표시
- [x] [건너뛰기] [재시도] 버튼 (각 교시별)
- [x] 상태 아이콘 (🕒 대기중, 🔍 감지중, ✅ 완료 등)
- [x] 하단 버튼 영역 UI
- [x] [📁 저장 경로 설정] 버튼
- [x] [📂 저장 폴더 열기] 버튼
- [x] `update_period_status()`: 교시 상태 업데이트
- [x] `on_skip_button()`: 건너뛰기 버튼 핸들러
- [x] `on_retry_button()`: 재시도 버튼 핸들러
- [x] `on_student_count_change()`: 학생 수 변경 핸들러
- [x] `show_alert()`: 알림창 표시

### 1.4 모니터 선택 기능
- [x] `utils/monitor.py` 생성
- [x] 모니터 목록 조회 함수 구현
- [x] 모니터 정보 반환 함수 구현 (해상도, 위치)

### 1.5 화면 캡처 기능
- [x] `features/capture.py` 생성
- [x] `ScreenCapture` 클래스 구현
- [x] `__init__()`: 모니터 ID 초기화
- [x] `capture()`: 화면 캡처 메서드
- [x] `get_monitor_info()`: 모니터 정보 조회
- [x] mss 라이브러리로 캡처 구현
- [x] 캡처 이미지 RGB 변환

### 1.6 얼굴 감지 기능
- [x] `features/face_detection.py` 생성
- [x] `FaceDetector` 클래스 구현
- [x] `__init__()`: GPU ID 설정
- [x] `initialize()`: InsightFace 모델 로드
- [x] `detect()`: 얼굴 감지 및 개수 반환
- [x] `cleanup()`: GPU 메모리 해제
- [x] InsightFace buffalo_l 모델 다운로드
- [x] GPU 감지 실패 시 CPU 전환 로직

### 1.7 파일 저장 기능
- [x] `features/file_manager.py` 생성
- [x] `FileManager` 클래스 구현
- [x] `__init__()`: 기본 저장 경로 설정
- [x] `ensure_folder_exists()`: 날짜 폴더 생성
- [x] `get_file_path(is_within_window)`: 파일 경로 생성 (파일명 규칙, 시간대 내/외 구분)
- [x] `_get_period_name()`: 교시명 반환 (Private)
- [x] `_validate_image()`: 이미지 유효성 검사 (Private)
- [x] `save_image(is_within_window)`: 이미지 저장 (시간대 기반 파일명)
- [x] 에러 처리 강화 (권한, 디스크 공간, 잘못된 입력)

### 1.8 스케줄링 기능
- [x] `features/scheduler.py` 생성
- [x] `CaptureScheduler` 클래스 구현
- [x] `__init__()`: 스케줄 목록 초기화
- [x] `add_schedule()`: 스케줄 추가
- [x] `is_in_capture_window()`: 캡처 시간대 확인
- [x] `start()`: 스케줄러 시작
- [x] `stop()`: 스케줄러 중지
- [x] `skip_period()`: 건너뛰기
- [x] `mark_completed()`: 교시 완료 처리 (캡처 성공 시)
- [x] `reset_period()`: 재시도용 초기화 (재시도 버튼 클릭 시)

### 1.9 알림창
- [x] `MainWindow.show_alert()` 메서드 구현
- [x] 성공 알림창 (캡처 완료) - alert_type="info"
- [x] 실패 알림창 (얼굴 감지 실패) - alert_type="warning"
- [x] 에러 알림창 (파일 저장 실패 등) - alert_type="error"

### 1.10 메인 프로그램 ✅
- [x] `main.py` 생성
- [x] 초기 설정 다이얼로그 표시 (InitDialog)
- [x] 메인 윈도우 시작 (MainWindow with config)
- [x] InitDialog를 독립 윈도우로 수정 (tk.Tk)
- [x] HiDPI/Retina 디스플레이 대응 (Windows ctypes)
- [x] InitDialog 화면 정중앙 배치
- [x] MainWindow 화면 정중앙 배치
- [x] Features 인스턴스 생성 (Capture, Detector, FileManager, Scheduler)
- [x] 프로그램 종료 시 cleanup 처리

---

## 📋 Phase 2: 제어 기능 및 통합 (Control & Integration)

### 2.1 CSV 로깅 ✅
- [x] `features/logger.py` 생성
- [x] `CSVLogger` 클래스 기본 구조
- [x] `_ensure_log_file()`: 로그 파일 생성 (헤더 포함)
- [x] `__init__()`: 로그 파일 경로 설정
- [x] `log_event()`: 이벤트 기록 메서드
- [x] CSV 구조 정의 (날짜, 시간, 항목, 상태, 감지인원, 기준인원, 파일명, 비고)
- [x] UTF-8-BOM 인코딩 (Excel 호환)

### 2.2 캡처 프로세스 통합
- [x] `MainWindow._on_capture_trigger(period)` 메서드 생성
- [x] `ScreenCapture.capture()` 호출 및 에러 처리
- [x] `FaceDetector.detect(image)` 호출 및 에러 처리
- [x] 캡처 모드별 비교 로직 구현
- [x] 정확 모드: `detected == threshold`
- [x] 유연 모드: `detected >= threshold * 0.9`
- [x] 조건 만족 시 처리
- [x] `FileManager.save_image()` 호출
- [x] `CSVLogger.log_event()` 호출
- [x] `Scheduler.mark_completed()` 호출
- [x] `update_period_status()` UI 업데이트
- [x] 성공 알림창 표시
- [x] 조건 불만족 시 처리
- [x] 이미지 메모리 해제
- [x] 실패 로그 기록
- [x] 10초 후 자동 재시도 (Scheduler)
- [x] `Scheduler`에 콜백 함수 등록
- [x] `Scheduler.start(root)` 호출하여 자동 트리거 활성화
- [x] 재시도 버튼 콜백 연결 (`on_retry_button()` → `_on_capture_trigger()`)
- [x] 캡처 프로세스 로그 추가 (단계별 추적)

### 2.3 인원 관리 (이벤트 핸들러 연결)
- [x] `MainWindow._on_student_count_change(*args)` 메서드 구현 (private)
- [x] 입력값 검증 (1~100)
- [x] `self.student_count` 업데이트
- [x] 기준 인원 재계산 (모드별)
- [x] UI 레이블 업데이트 (Helper 메서드 호출)
- [x] trace_add 이벤트 연결 (_on_student_count_change)

### 2.4 캡처 모드 전환
- [x] `MainWindow._on_mode_change(event)` 메서드 구현 (private)
- [x] `self.mode` 업데이트
- [x] 기준 인원 재계산 (Helper 메서드 호출)
- [x] UI 업데이트 (모드별 표시)
- [x] Combobox 이벤트 연결 (_on_mode_change)

### 2.5 건너뛰기 기능 통합 ✅
- [x] `MainWindow.on_skip_button(period)` 메서드 구현
- [x] `Scheduler.skip_period(period)` 호출
- [x] `update_period_status()` 호출 (상태: 건너뛰기)
- [x] `CSVLogger.log_event()` 호출

### 2.6 재시도 기능 통합 ✅
- [x] `MainWindow.on_retry_button(period)` 메서드 구현
- [x] `Scheduler.is_in_capture_window(period)` 시간대 확인
- [x] `Scheduler.reset_period(period)` 상태 초기화
- [x] `update_period_status()` UI 업데이트
- [x] `CSVLogger.log_event()` 호출

### 2.7 캡처 실패 알림창 추가 ✅
- [x] `_process_capture_failure()` 메서드에 `show_alert()` 호출 추가

---

## 📋 Phase 3: 추가 기능 (Additional Features)

### 3.1 설정 저장/로드 ✅
- [x] `utils/config.py` 생성
- [x] `Config` 클래스 구현
- [x] `load()`: 설정 파일 읽기
- [x] `save()`: 설정 파일 쓰기
- [x] `get()`: 설정 값 조회
- [x] `set()`: 설정 값 저장
- [x] config.json 구조 정의
- [x] 프로그램 시작 시 설정 로드 (InitDialog에서 Config.load() 호출)
- [x] 프로그램 종료 시 설정 저장 (InitDialog에서 Config.save() 호출)
- [x] 설정 파일 없을 시 기본값 사용
- [x] MainWindow에 Config.save() 통합
- [x] main.py에 config_manager 전달

### 3.2 저장 경로 변경 기능 연결 ✅
- [x] Config.set()으로 설정 저장
- [x] FileManager 인스턴스 재생성
- [x] CSVLogger 인스턴스 재생성

### 3.3 모니터 변경 기능 연결 ✅
- [x] 콤보박스 UI로 변경 (버튼 → 콤보박스)
- [x] `_on_monitor_change()` 핸들러 구현
- [x] Config.set()으로 설정 저장
- [x] ScreenCapture 인스턴스 재생성

---

## 📋 Phase 4: 최적화 및 마무리 (Optimization & Finalization)

### 4.1 코드 품질 검토
- [x] rules.md 체크리스트 전수 점검 (16장)
- [x] 중복 코드 제거 및 리팩토링

### 4.2 예외 처리 강화
- [x] 1. `features/exceptions.py` 파일 생성 및 커스텀 예외 클래스 구현
- [x] 2. 기존 코드를 커스텀 예외로 교체
- [x] 3. `gui/main_window.py`에 사용자 알림 추가
  - `InsufficientStorageError` catch → 디스크 공간 부족 알림
  - `InvalidMonitorError` catch → 모니터 재선택 알림
  - `FilePermissionError` catch → 저장 경로 변경 알림
  - `ModelLoadError` catch → InsightFace 설치 확인 알림

### 4.3 성능 최적화
- [x] 1. 인스턴스 재사용 확인 (FaceDetector, mss)
- [x] 2. 이미지 메모리 명시적 해제 확인 (`del image`)
- [x] 3. 실제 캡처 테스트 및 로그 타임스탬프로 성능 확인

### 4.4 EXE 빌드
- [x] PyInstaller 설치 및 기본 빌드 테스트
- [x] InsightFace 모델 포함 및 경로 문제 해결
- [x] .spec 파일 작성 및 최적화
- [x] EXE 실행 테스트
- [x] InsightFace 모델 자동 로드 동작 확인
- [x] build.bat 스크립트 작성

### 4.5 문서화
- [x] README.md 작성
  - 프로젝트 소개 및 주요 기능
  - 시스템 요구사항 (EXE 실행 vs Python 소스 실행)
  - 설치 방법
    - 방법 1: EXE 파일 실행 (권장)
    - 방법 2: Python 소스 실행 (개발자용)
  - GPU 드라이버 및 CUDA Toolkit 설치 가이드
  - 프로그램 실행 방법
  - 초기 설정 가이드 (모니터 선택, 저장 경로, 캡처 모드 등)
  - 사용 방법 (교시별 캡처, 건너뛰기, 재시도 등)
  - 파일 저장 구조 및 규칙
  - 트러블슈팅 (7가지 주요 문제 해결)
    - 얼굴 감지 실패
    - GPU 인식 실패
    - 파일 저장 실패
    - 프로그램 느림
    - InsightFace 모델 오류
    - 프로그램 실행 안 됨
    - 설정이 저장 안 됨
  - 개발자 정보 (프로젝트 구조, EXE 빌드, 기술 스택)
- [x] requirements.txt 최종 확인

### 4.6 최종 검증 및 배포 준비
- [ ] 실제 환경에서 최종 테스트 (듀얼 모니터, Zoom 화면)

### 4.7 릴리스 관리
- [ ] 최종 버전 태그 생성 (v1.0.0)
- [ ] GitHub Release 작성

---

## 💡 개발 팁

### Phase별 개발 순서
- **Phase 1 (1.1~1.8)**: 핵심 기능 완료 ✅
  - GUI 레이아웃, 화면 캡처, 얼굴 감지, 파일 저장, 스케줄러 구현 완료
- **Phase 1 (1.9~1.10)**: 알림창 및 메인 프로그램 통합
- **Phase 2**: 제어 기능 (건너뛰기, 재시도, 로깅 등)
- **Phase 3**: 설정 저장/로드 및 추가 기능
- **Phase 4**: 최적화, 테스트, 문서화, 배포

### 개발 시 주의사항
- 각 Phase 시작 전 `docs/rules.md` 재확인
- 기능 구현 후 반드시 테스트 스크립트 작성
- architecture.md 기준으로 메서드 시그니처 정확히 구현

---

**문서 버전**: 2.3
**최종 수정일**: 2025-11-26
**주요 변경사항**:
- Phase 4.4 문서화 항목 상세화 및 통합
  - README.md 작성 시 포함할 내용 명시 (설치 가이드, 사용법, 트러블슈팅)
  - 기존 4.5의 가이드 작성 항목들을 4.4 README.md 작성에 통합
- Phase 4.5 "최종 검증 및 배포 준비"로 명확화
  - 실제 테스트 및 동작 검증에 집중
  - 문서화 작업은 4.4에서 완료