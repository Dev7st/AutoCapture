# 개발 규칙 (Development Rules)

이 문서는 출결 관리 자동 캡처 프로그램 개발 시 준수해야 할 규칙을 정의합니다.

---

## 1. 프로젝트 구조 규칙

### 1.1 폴더 구조
```
attendance_capture/
├─ docs/              # 문서만
├─ core/              # 핵심 비즈니스 로직만
├─ gui/               # GUI 관련 코드만
├─ utils/             # 유틸리티 함수만
└─ tests/             # 테스트 코드만 (선택)
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
from core.capture import ScreenCapture
from utils.config import Config
```

### 3.5 함수 길이
- **최대 50줄**
- 50줄 넘으면 분리

### 3.6 클래스 길이
- **최대 500줄**
- 500줄 넘으면 분리

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
```python
# TODO: GPU 메모리 부족 시 자동으로 CPU 모드 전환
# FIXME: 가끔 얼굴 감지가 실패하는 버그 수정 필요
# HACK: 임시 해결책, 나중에 리팩토링 필요
```

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

### 8.2 파일 저장
```python
# ✅ 좋은 예: with 문 사용
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# ❌ 나쁜 예: close() 잊을 수 있음
f = open(file_path, 'w')
f.write(content)
f.close()
```

### 8.3 인코딩 명시
```python
# CSV 파일은 UTF-8-BOM (Excel 호환)
with open(log_path, 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
```

---

## 9. Git 커밋 규칙

### 9.1 커밋 메시지 형식
```
<type>: <subject>

<body> (선택사항)
```

### 9.2 Type 종류
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가
- `chore`: 기타 (빌드, 설정 등)

### 9.3 예시
```bash
# ✅ 좋은 예
feat: InsightFace 얼굴 감지 기능 구현
fix: 듀얼 모니터 인덱스 오류 수정
docs: README에 설치 방법 추가

# ❌ 나쁜 예
update
fixed bug
asdf
```

### 9.4 커밋 단위
- **작은 단위로 자주 커밋**
- 하나의 기능/수정 = 하나의 커밋

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
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 14.3 IDE 설정 (VSCode/Cursor)
```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [120]
}
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
- [ ] Import 순서가 맞는가?
- [ ] 테스트 했는가?
- [ ] Git 커밋 메시지가 명확한가?

---

**이 규칙을 따라 일관성 있는 코드를 작성합시다! 🚀**

**문서 버전**: 1.0  
**최종 수정일**: 2025-10-21