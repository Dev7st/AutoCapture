# 개발 규칙 (Development Rules)

이 문서는 출결 관리 자동 캡처 프로그램 개발 시 준수해야 할 규칙을 정의합니다.

---

## 1. 프로젝트 구조 규칙

### 1.1 폴더 구조

**프로젝트 루트: `capture/`**

```
capture/                                    # 프로젝트 루트
├─ docs/                                    # 📁 문서
│  ├─ requirements.md                       # 요구사항 명세서
│  ├─ rules.md                              # 개발 규칙
│  ├─ architecture.md                       # 기술 설계서
│  └─ tasks.md                              # Task 체크리스트
│
├─ features/                                # 📁 핵심 기능 (비즈니스 로직)
│  ├─ __init__.py
│  ├─ capture.py                            # 화면 캡처
│  ├─ face_detection.py                     # 얼굴 감지
│  ├─ file_manager.py                       # 파일 저장
│  ├─ logger.py                             # CSV 로깅
│  └─ scheduler.py                          # 스케줄링
│
├─ gui/                                     # 📁 GUI
│  ├─ __init__.py
│  ├─ main_window.py                        # 메인 윈도우
│  └─ dialogs.py                            # 초기 설정 다이얼로그
│
├─ utils/                                   # 📁 유틸리티
│  ├─ __init__.py
│  ├─ config.py                             # 설정 관리
│  └─ monitor.py                            # 모니터 선택
│
├─ assets/                                  # 📁 리소스
│  └─ icons/                                # 아이콘 (시스템 트레이 등)
│     └─ .gitkeep                           # 빈 폴더 유지용
│
├─ tests/                                   # 📁 테스트 (선택)
│  ├─ __init__.py
│  ├─ test_capture.py
│  ├─ test_face_detection.py
│  └─ test_scheduler.py
│
├─ main.py                                  # 프로그램 진입점
├─ __init__.py                              # 패키지 초기화
├─ .gitignore                               # Git 제외 파일
├─ requirements.txt                         # Python 패키지 목록
└─ README.md                                # 프로젝트 소개
```

### 1.2 파일 분리 원칙
- **하나의 파일 = 하나의 클래스** (가능한 한)
- 파일 크기: 최대 500줄
- 관련 없는 기능은 별도 파일로 분리

### 1.3 __init__.py
- 모든 폴더에 `__init__.py` 필수
- 외부로 노출할 것만 `__all__`에 정의

---

## 2. 네이밍 규칙

### 2.1 파일명
- **형식**: `snake_case.py`
- **예시**:
  - ✅ `face_detection.py`
  - ✅ `main_window.py`
  - ❌ `FaceDetection.py`
  - ❌ `mainWindow.py`

### 2.2 클래스명
- **형식**: `PascalCase`
- **예시**:
  - ✅ `FaceDetector`
  - ✅ `MainWindow`
  - ✅ `CaptureScheduler`
  - ❌ `faceDetector`
  - ❌ `main_window`

### 2.3 함수/메서드명
- **형식**: `snake_case`
- **동사로 시작**
- **예시**:
  - ✅ `detect_faces()`
  - ✅ `capture_screen()`
  - ✅ `save_image()`
  - ❌ `DetectFaces()`
  - ❌ `faceCount()`

### 2.4 변수명
- **형식**: `snake_case`
- **의미있는 이름 사용**
- **예시**:
  - ✅ `face_count`
  - ✅ `capture_time`
  - ✅ `student_count`
  - ❌ `fc`
  - ❌ `x`
  - ❌ `temp`

### 2.5 상수명
- **형식**: `UPPER_SNAKE_CASE`
- **파일 상단에 정의**
- **예시**:
  - ✅ `MAX_RETRY_COUNT = 10`
  - ✅ `DEFAULT_SAVE_PATH = "C:/IBM 비대면"`
  - ✅ `CAPTURE_INTERVAL = 10`
  - ❌ `maxRetryCount = 10`

### 2.6 Private 메서드/변수
- **형식**: `_underscore`로 시작
- **예시**:
  - ✅ `_internal_method()`
  - ✅ `_temp_buffer`
  - ❌ `__double_underscore()` (특별한 경우만)

---

## 3. 코딩 스타일

### 3.1 들여쓰기
- **4 spaces** (Tab 아님)
- IDE 설정으로 자동화

### 3.2 줄 길이
- **최대 120자**
- 넘으면 줄바꿈

### 3.3 공백
```python
# ✅ 좋은 예
def calculate_total(a, b, c):
    result = (a + b) * c
    return result

# ❌ 나쁜 예
def calculate_total(a,b,c):
    result=(a+b)*c
    return result
```

### 3.4 Import 순서
```python
# 1. 표준 라이브러리
import os
import sys
from datetime import datetime

# 2. 외부 라이브러리
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis

# 3. 내부 모듈
from features.capture import ScreenCapture
from utils.config import Config
```

### 3.5 함수 길이
- **최대 50줄**
- 50줄 넘으면 분리

**분리 방법:**
1. 논리적 단위로 쪼개기
2. Helper 함수로 추출
3. Private 메서드로 분리

**예시:**
```python
# ❌ 나쁜 예: 100줄 함수
def process_capture():
    # 화면 캡처 (20줄)
    monitor = get_monitor()
    screenshot = capture(monitor)
    # ... 20줄
    
    # 얼굴 감지 (30줄)
    model = load_model()
    faces = detect(screenshot)
    # ... 30줄
    
    # 파일 저장 (20줄)
    path = generate_path()
    save(screenshot, path)
    # ... 20줄
    
    # 로그 기록 (30줄)
    log_data = prepare_log()
    write_log(log_data)
    # ... 30줄

# ✅ 좋은 예: 분리
def process_capture():
    """메인 캡처 프로세스"""
    image = _capture_screen()       # 20줄 → 별도 함수
    faces = _detect_faces(image)    # 30줄 → 별도 함수
    _save_image(image)              # 20줄 → 별도 함수
    _log_result(faces)              # 30줄 → 별도 함수

def _capture_screen():
    """화면 캡처 (Private 함수)"""
    monitor = get_monitor()
    screenshot = capture(monitor)
    return screenshot

def _detect_faces(image):
    """얼굴 감지 (Private 함수)"""
    model = load_model()
    faces = detect(image)
    return faces
```

### 3.6 클래스 길이
- **최대 500줄**
- 500줄 넘으면 분리

**분리 방법:**
1. 책임별로 클래스 분리
2. Mixin 클래스 활용
3. 별도 모듈로 추출

**예시:**
```python
# ❌ 나쁜 예: 하나의 거대 클래스
class FaceDetector:
    def __init__(self): pass
    def detect(self): pass           # 100줄
    def preprocess(self): pass       # 100줄
    def postprocess(self): pass      # 100줄
    def save_result(self): pass      # 100줄
    def load_model(self): pass       # 100줄
    # ... 총 500줄 초과

# ✅ 좋은 예: 책임별 분리
class FaceDetector:
    """얼굴 감지만 담당"""
    def __init__(self): pass
    def detect(self): pass

class ImagePreprocessor:
    """이미지 전처리 담당"""
    def preprocess(self): pass

class ResultSaver:
    """결과 저장 담당"""
    def save(self): pass
```

---

## 4. 주석 및 문서화

### 4.1 Docstring (필수)
```python
def detect_faces(image: np.ndarray, threshold: float = 0.5) -> int:
    """
    이미지에서 얼굴을 감지하고 개수를 반환합니다.
    
    Args:
        image (np.ndarray): 입력 이미지 (RGB)
        threshold (float): 감지 임계값 (0.0~1.0)
    
    Returns:
        int: 감지된 얼굴 개수
    
    Raises:
        ValueError: 이미지가 None이거나 비어있을 때
    
    Example:
        >>> image = cv2.imread("test.jpg")
        >>> count = detect_faces(image)
        >>> print(count)
        5
    """
    pass
```

### 4.2 클래스 Docstring
```python
class FaceDetector:
    """
    InsightFace를 사용한 얼굴 감지 클래스.
    
    GPU를 활용하여 이미지에서 얼굴을 감지합니다.
    
    Attributes:
        gpu_id (int): 사용할 GPU ID (-1이면 CPU)
        model: InsightFace 모델 인스턴스
    
    Example:
        >>> detector = FaceDetector(gpu_id=0)
        >>> count = detector.detect(image)
    """
    pass
```

### 4.3 인라인 주석
```python
# ✅ 좋은 예: 왜 이렇게 했는지 설명
# InsightFace는 RGB 순서를 요구하므로 BGR->RGB 변환
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ❌ 나쁜 예: 코드가 하는 일을 반복
# 이미지를 RGB로 변환
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
```

### 4.4 TODO 주석

**위치:** 해당 코드 바로 위 또는 함수/클래스 docstring 다음

```python
# 함수 시작 부분 (docstring 다음)
def detect_faces(image):
    """얼굴을 감지합니다."""
    # TODO: GPU 메모리 부족 시 자동으로 CPU 모드 전환
    # FIXME: 가끔 얼굴 감지가 실패하는 버그 수정 필요
    pass

# 해당 코드 바로 위
result = risky_operation()
# FIXME: 가끔 실패하는 버그 수정 필요
process(result)

# 클래스 시작 부분
class FaceDetector:
    """얼굴 감지 클래스"""
    # TODO: 다중 GPU 지원 추가
    pass
```

**TODO 주석 종류:**
- `TODO`: 나중에 구현할 기능
- `FIXME`: 알려진 버그, 반드시 수정 필요
- `HACK`: 임시 해결책, 나중에 리팩토링 필요
- `NOTE`: 중요한 설명

---

## 5. 에러 처리

### 5.1 기본 원칙
- **모든 외부 호출은 try-except**로 감싸기
- 파일 I/O, 네트워크, GPU 연산 등

### 5.2 예외 처리 패턴
```python
# ✅ 좋은 예
def load_image(path: str) -> Image:
    """이미지 파일을 로드합니다."""
    try:
        image = Image.open(path)
        return image
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {path}")
        raise
    except Exception as e:
        logger.error(f"이미지 로드 실패: {e}")
        raise

# ❌ 나쁜 예
def load_image(path: str) -> Image:
    image = Image.open(path)  # 에러 처리 없음
    return image
```

### 5.3 로깅
```python
import logging

logger = logging.getLogger(__name__)

# 에러 발생 시 반드시 로깅
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"작업 실패: {e}", exc_info=True)
    raise
```

---

## 6. Type Hints (권장)

### 6.1 함수 시그니처
```python
# ✅ 좋은 예
def capture_screen(monitor_id: int) -> np.ndarray:
    pass

def save_image(image: np.ndarray, path: str) -> bool:
    pass

# ❌ 나쁜 예
def capture_screen(monitor_id):
    pass
```

### 6.2 변수 Type Hints
```python
from typing import List, Dict, Optional

# 복잡한 타입에만 사용
students: List[str] = []
config: Dict[str, any] = {}
result: Optional[int] = None
```

---

## 7. 클래스 설계 원칙

### 7.1 단일 책임 원칙
- **하나의 클래스 = 하나의 책임**
```python
# ✅ 좋은 예
class FaceDetector:
    """얼굴 감지만 담당"""
    pass

class ScreenCapture:
    """화면 캡처만 담당"""
    pass

# ❌ 나쁜 예
class FaceDetectorAndCapture:
    """얼굴 감지 + 화면 캡처 → 책임 과다"""
    pass
```

### 7.2 생성자 규칙
```python
class FaceDetector:
    def __init__(self, gpu_id: int = 0):
        """
        생성자에서는 초기화만.
        무거운 작업(모델 로드)은 별도 메서드로.
        """
        self.gpu_id = gpu_id
        self.model = None  # 아직 로드 안 함
    
    def initialize(self):
        """모델 로드 (무거운 작업)"""
        self.model = FaceAnalysis()
        self.model.prepare(ctx_id=self.gpu_id)
```

### 7.3 메서드 순서
```python
class Example:
    # 1. 생성자
    def __init__(self):
        pass
    
    # 2. Public 메서드
    def public_method(self):
        pass
    
    # 3. Private 메서드
    def _private_method(self):
        pass
    
    # 4. Property
    @property
    def some_property(self):
        pass
```

---

## 8. 파일 I/O 규칙

### 8.1 경로 처리
```python
from pathlib import Path

# ✅ 좋은 예: pathlib 사용
save_path = Path("C:/IBM 비대면")
date_folder = save_path / "251020"
date_folder.mkdir(parents=True, exist_ok=True)

# ❌ 나쁜 예: 문자열 조합
save_path = "C:/IBM 비대면" + "/" + "251020"
```

### 8.2 파일 저장 (with 문)
```python
# ✅ 좋은 예: with 문 사용
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# ❌ 나쁜 예: close() 잊을 수 있음
f = open(file_path, 'w')
f.write(content)
f.close()
```

**with 문 장점:**
- 파일이 자동으로 닫힘 (메모리 누수 방지)
- 예외 발생 시에도 안전하게 닫힘
- 코드 간결

### 8.3 인코딩 명시
```python
# CSV 파일은 UTF-8-BOM (Excel 호환)
with open(log_path, 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
```

---

## 9. Git 전략

### 9.1 브랜치 전략 (GitHub Flow)
이 프로젝트는 **GitHub Flow** 전략을 사용합니다.

**브랜치 구조:**
- `main`: 항상 배포 가능한 안정적인 버전
- `feature/*`: 기능 개발용 임시 브랜치

**작업 흐름:**
```bash
# 1. 새 기능 시작
git checkout -b feature/face-detection

# 2. 해당 브랜치에서 개발 + 테스트
git add .
git commit -m "feat: 얼굴 감지 구현"
git commit -m "test: 얼굴 감지 테스트 추가"

# 3. 완료되면 main에 병합
git checkout main
git merge feature/face-detection

# 4. feature 브랜치 삭제
git branch -d feature/face-detection

# 5. 큰 단위 완료 시 태그
git tag v0.1.0
git push origin main --tags
```

**feature 브랜치 네이밍:**
- `feature/face-detection` - 얼굴 감지 기능
- `feature/gui-main-window` - GUI 메인 윈도우
- `feature/scheduler` - 스케줄러 기능

### 9.2 커밋 메시지 형식
```
<type>: <subject>

<body> (선택사항)
```

**Type 종류:**
- `feat`: 새 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 기타 (빌드, 설정 등)

**예시:**
```bash
# ✅ 좋은 예
feat: InsightFace 얼굴 감지 기능 구현
fix: 듀얼 모니터 인덱스 오류 수정
docs: README에 설치 방법 추가
refactor: FaceDetector 클래스 분리

# ❌ 나쁜 예
update
fixed bug
asdf
수정함
```

### 9.3 커밋 단위
- **작은 단위로 자주 커밋**
- 하나의 기능/수정 = 하나의 커밋
- 의미 있는 단위로 분리

---

## 10. 테스트 규칙 (선택사항)

### 10.1 테스트 파일명
```
tests/
├─ test_capture.py
├─ test_face_detection.py
└─ test_scheduler.py
```

### 10.2 테스트 함수명
```python
def test_face_detection_with_valid_image():
    """정상 이미지로 얼굴 감지 테스트"""
    pass

def test_face_detection_with_empty_image():
    """빈 이미지로 얼굴 감지 테스트"""
    pass
```

---

## 11. 성능 최적화 규칙

### 11.1 GPU 메모리 관리
```python
class FaceDetector:
    def cleanup(self):
        """GPU 메모리 해제"""
        if self.model is not None:
            del self.model
            self.model = None
```

### 11.2 이미지 처리
```python
# 큰 이미지는 처리 후 즉시 삭제
image = capture_screen()
result = process_image(image)
del image  # 메모리 해제
```

---

## 12. 보안 규칙

### 12.1 민감 정보
```python
# ❌ 나쁜 예: 코드에 하드코딩
API_KEY = "abc123"

# ✅ 좋은 예: 환경변수 또는 설정 파일
import os
API_KEY = os.getenv("API_KEY")
```

### 12.2 파일 권한
```python
# 설정 파일은 읽기 전용으로
os.chmod(config_path, 0o444)
```

---

## 13. Claude Code 사용 시 주의사항

### 13.1 프롬프트 작성
```
# ✅ 좋은 예
"FaceDetector 클래스에 cleanup() 메서드를 추가해줘.
GPU 메모리를 해제하는 기능이야."

# ❌ 나쁜 예
"얼굴 감지 좀 수정해줘"
```

### 13.2 코드 검토
- Claude Code가 생성한 코드는 **반드시 검토**
- 이 rules.md에 맞는지 확인
- 테스트 후 커밋

---

## 14. 개발 환경 설정

### 14.1 Python 버전
- **Python 3.10.11** 고정

### 14.2 가상환경

**venv 사용 시:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**conda 사용 시:**
```bash
conda create -n capture python=3.10.11
conda activate capture
pip install -r requirements.txt
```

---

## 15. 금지 사항

### 15.1 절대 하지 말 것
- ❌ `print()` 디버깅 (logger 사용)
- ❌ 하드코딩 (상수 사용)
- ❌ 전역 변수 남발
- ❌ 주석 없는 복잡한 로직
- ❌ 에러 무시 (`except: pass`)
- ❌ Magic Number (의미 없는 숫자)

### 15.2 예시
```python
# ❌ 나쁜 예
def calculate():
    x = 10  # Magic Number
    if y > 100:  # Magic Number
        pass

# ✅ 좋은 예
MAX_RETRY = 10
THRESHOLD = 100

def calculate():
    retry_count = MAX_RETRY
    if value > THRESHOLD:
        pass
```

---

## 16. 마지막 체크리스트

코드 커밋 전 확인:
- [ ] Docstring 작성했는가?
- [ ] Type Hints 추가했는가?
- [ ] 에러 처리 했는가?
- [ ] 변수명이 명확한가?
- [ ] 함수가 50줄 이하인가?
- [ ] 클래스가 500줄 이하인가?
- [ ] Import 순서가 맞는가?
- [ ] 테스트 했는가?
- [ ] Git 커밋 메시지가 명확한가?
- [ ] feature 브랜치에서 작업했는가?

---

**이 규칙을 따라 일관성 있는 코드를 작성합시다! 🚀**

**문서 버전**: 2.0
**최종 수정일**: 2025-10-22
**주요 변경사항**:
- 폴더 구조 수정 (core → features, src 삭제)
- 함수/클래스 길이 초과 시 분리 방법 추가
- TODO 주석 위치 명확화
- Git 전략을 GitHub Flow로 명확히 정의
- Conda 가상환경 추가
- IDE 설정 제거 (Cursor 사용)