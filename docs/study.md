# 개발 문서 구조 가이드

## 📄 1. 요구사항 정의서 (requirements.md)

**목적**: "무엇을" 만들 것인가?, "왜" 이 기능이 필요한가?, "언제" 어떤 동작을 하는가?

**포함 내용**:
- 기능 목록
- 화면 설계
- 사용 시나리오
- 예외 처리
- 성능 요구사항

**대상 독자**: 기획자(요구사항 확인), 담당자(기능 검토), 개발자(무엇을 만들지), Claude Code(전체 맥락 파악)

## 📄 2. 기술 설계서 (architecture.md)

**목적**: "어떻게" 만들 것인가?

**포함 내용**:
- 아키텍처 설계
- 클래스 구조
- 함수 명세
- 데이터 흐름

**대상 독자**: 개발자, Claude Code

## 📄 3. Task 분해 문서 (tasks.md)

**목적**: "무엇부터 먼저" 만들 것인가?

**포함 내용**:
- 개발 순서
- Task 목록
- 의존성 관계
- 체크리스트

**대상 독자**: Claude Code

## 📄 4. 개발 규칙 (rules.md)

**목적**: "어떤 규칙으로" 만들 것인가?

**포함 내용**:
- 코딩 컨벤션
- 파일 구조 규칙
- 네이밍 규칙
- 개발 원칙

**대상 독자**: Claude Code

---

## 📚 MVC 패턴 (Model-View-Controller)

### 개요

소프트웨어를 3개 레이어로 분리하는 아키텍처 패턴
```
┌─────────┐     ┌────────────┐     ┌───────┐
│  View   │ ←─→ │ Controller │ ←─→ │ Model │
│  (UI)   │     │  (Logic)   │     │ (Data)│
└─────────┘     └────────────┘     └───────┘
```

### 각 레이어 역할

**Model (데이터)**
- 데이터와 비즈니스 로직
- 데이터베이스, 파일, 설정 등
- 예: `Config`, `CaptureResult` 데이터 구조

**View (화면)**
- 사용자 인터페이스
- 데이터 표시만 담당
- 예: `MainWindow`, `InitDialog`

**Controller (제어)**
- Model과 View 중간 다리
- 사용자 입력 처리
- 비즈니스 로직 실행
- 예: `FaceDetector`, `CaptureScheduler`

### 핵심 원칙

1. **분리**: 각 레이어는 독립적
2. **단방향**: View → Controller → Model
3. **재사용**: Controller는 다른 View에서 재사용 가능

**참고 사이트**: https://mundol-colynn.tistory.com/147

---

## 🔍 Python 클래스 변수의 이해

파이썬 클래스에서 **`self`를 쓰는 변수**와 **쓰지 않는 변수**의 근본적인 차이는 그 변수가 **어디에 속하는지(소속)**, 그리고 **어떻게 공유되는지(범위)**입니다.

### 1. `self.` 변수 (인스턴스 변수) 👤

`self.변수명` 형태로 선언된 변수는 **인스턴스 변수(Instance Variable)**입니다.

| 항목 | 내용 |
| :--- | :--- |
| **소속** | 클래스를 통해 만들어진 **각각의 객체(인스턴스)** |
| **범위** | 각 인스턴스에만 해당되며, **인스턴스마다 고유한 값**을 가짐 (공유되지 않음) |
| **사용** | 객체의 고유한 속성 저장 (예: 사람의 이름, 자동차의 색상) |
| **선언 위치** | 주로 **`__init__`** 메서드 내에서 정의됨 |

**예시**:
인스턴스 A의 `self.name`과 인스턴스 B의 `self.name`은 완전히 다른 값입니다.

### 2. `self`를 쓰지 않는 변수 🏛️

`self`를 쓰지 않는 변수는 선언 위치에 따라 **클래스 변수** 또는 **지역 변수**로 나뉩니다.

#### A. 클래스 변수 (클래스 본체에 선언)

| 항목 | 내용 |
| :--- | :--- |
| **소속** | **클래스 자체** |
| **범위** | 해당 클래스의 **모든 인스턴스가 값을 공유**함 |
| **사용** | 모든 객체가 공유해야 하는 공통적인 값 (예: 총 인스턴스 개수, 종(Species) 정보) |
| **접근** | `클래스명.변수명` 또는 `인스턴스명.변수명` |

#### B. 지역 변수 (메서드 내에 선언)

| 항목 | 내용 |
| :--- | :--- |
| **소속** | 해당 **메서드(함수)** |
| **범위** | 메서드가 실행되는 동안에만 존재하며, **메서드 종료 시 사라짐** |
| **사용** | 메서드 내에서 임시적인 계산이나 처리를 위한 값 |
| **접근** | 해당 메서드 외부에서 접근 불가 |

---

# ✨ 파이썬 타입 힌트 (Type Hint)

## 📌 1. 타입 힌트란 무엇인가요?

파이썬은 **동적 타입 언어**이지만, 타입 힌트는 코드의 **가독성과 유지보수성**을 높이기 위해 개발자가 변수, 함수 매개변수, 반환 값 등에 **원하는 데이터 타입(유형)을 명시적으로 표시**하는 기능입니다.

  * **역할:** 코드를 실행하는 **런타임(Runtime)에는 아무런 영향**을 주지 않습니다. 대신, 개발 도구나 외부 도구(**Mypy** 등 정적 타입 검사기)가 코드를 분석하여 잠재적인 오류를 미리 감지하는 데 도움을 줍니다.
  * **목적:** 개발자가 코드를 더 쉽게 이해하고, 협업하며, 버그 발생 가능성을 줄이는 데 있습니다.

## 📝 2. 기본 사용 예시

타입 힌트는 콜론(`:`)과 화살표(`->`)를 사용하여 명시합니다.

### 가. 변수 (Variables)

변수 이름 뒤에 콜론(`:`)을 붙여 타입을 명시합니다.

```python
age: int = 30
name: str = "Alice"
is_active: bool = True
price: float = 19.99
```

### 나. 함수 (Functions)

  * **매개변수:** 매개변수 이름 뒤에 `: Type`을 붙입니다.
  * **반환 값:** 매개변수 목록을 닫는 괄호 뒤에 `-> Type`을 붙입니다.

<!-- end list -->

```python
def add_numbers(a: int, b: int) -> int:
    """두 정수를 더하여 결과를 반환합니다."""
    return a + b

def greet(name: str) -> str:
    """이름을 받아 환영 메시지를 반환합니다."""
    return f"안녕하세요, {name}님!"

def process_data(data: str):
    """반환 값이 없을 경우 -> None을 명시할 수 있습니다."""
    print(f"데이터 처리 중: {data}")
```

## ⚙️ 3. `typing` 모듈을 사용한 복잡한 타입 정의

리스트, 딕셔너리, 튜플 등 컬렉션 타입이나 복잡한 구조를 정의할 때는 내장된 `typing` 모듈을 사용합니다.

| 타입 | 설명 | 예시 코드 |
| :--- | :--- | :--- |
| **List** | 리스트의 요소 타입 명시 | `data: List[int] = [1, 2, 3]` |
| **Dict** | 키와 값의 타입 명시 | `user: Dict[str, str] = {"name": "Bob", "city": "Seoul"}` |
| **Tuple** | 각 요소의 타입 명시 | `point: Tuple[float, float] = (10.5, 20.2)` |
| **Optional** | 해당 타입이거나 `None`일 수 있음 | `maybe_name: Optional[str] = None` |
| **Union** | 여러 타입 중 하나일 수 있음 | `value: Union[int, str]` (Python 3.10+에서는 `int | str`로 사용 가능) |

```python
from typing import List, Dict, Optional, Union

# 정수 리스트
def calculate_sum(numbers: List[int]) -> int:
    return sum(numbers)

# 문자열 키와 실수 값을 가지는 딕셔너리
def get_config(key: str) -> Optional[float]:
    config: Dict[str, float] = {"rate": 0.5, "factor": 1.2}
    return config.get(key)
```

## ⚠️ 4. 핵심 정리 및 주의사항

  * **파이썬 실행에 영향 없음:** 타입 힌트를 지키지 않아도 파이썬 코드는 실행됩니다. (예: `a: int = "hello"`)
  * **정적 검사 도구 사용 권장:** 타입 힌트의 효과를 극대화하려면 **Mypy**와 같은 외부 정적 타입 검사 도구를 사용해야 합니다.
  * **가독성 향상:** 코드의 의도를 명확하게 전달하여 이해하기 쉬운 코드를 만듭니다.

---

## 🏷️ Git 태그(Tag) 관리

### 📌 태그(Tag)란?

Git에서 **특정 커밋에 이름표를 붙여서 기록**하는 기능입니다. 주로 배포 버전이나 중요한 마일스톤<!--프로젝트의 중간 목표 지점, 예: Phase 1.2 완료-->을 표시할 때 사용합니다.

### ✅ 태그가 필요한 이유

1. **버전 히스토리 추적**
   - 특정 시점의 완성된 기능 스냅샷 저장
   - "Phase 1.2가 정확히 어느 커밋인가?" → 태그로 바로 확인 가능

2. **롤백 용이성**
   - 문제 발생 시 특정 버전으로 빠르게 복구
   - `git checkout v0.1.2` 한 번에 Phase 1.2 상태로 복구

3. **릴리즈 관리**
   - GitHub Releases 기능과 연동 가능
   - 실행 파일 배포 시 버전별로 관리

4. **개발 마일스톤 기록**
   - 프로젝트 진행 상황을 한눈에 파악
   - 개발 문서와 실제 코드 버전 매핑

### 🏷️ 태그 버전 네이밍 전략 (Semantic Versioning)

```
v<major>.<minor>.<patch>
```

**예시:**
- `v0.1.0`: Phase 1.1 완료 (InitDialog 기본 UI)
- `v0.1.1`: Phase 1.1 버그픽스
- `v0.1.2`: Phase 1.2 완료 (InitDialog 검증 로직)
- `v0.2.0`: Phase 2.1 완료 (MainWindow 기본 틀)
- `v1.0.0`: 전체 프로젝트 완성 (첫 배포)

**규칙:**
- **major** (v1.0.0): 전체 프로젝트 완성 또는 대규모 변경
- **minor** (v0.1.0): Phase 단위 기능 완료
- **patch** (v0.1.1): 버그픽스, 작은 수정

---

## 🎮 GPU 가속 관련 개념

### 📌 NVIDIA 드라이버 vs CUDA Toolkit

딥러닝 프로그램에서 GPU를 사용하려면 여러 소프트웨어 계층이 필요합니다. 각각의 역할을 이해하면 GPU 설정과 문제 해결이 쉬워집니다.

### 🔧 NVIDIA 드라이버

**역할:**
- GPU 하드웨어와 운영체제(Windows)를 연결하는 **기본 소프트웨어**
- GPU가 컴퓨터에서 인식되고 기본 작동하도록 하는 필수 프로그램

**기능:**
- GPU 하드웨어 인식 및 제어
- DirectX, OpenGL 등 그래픽 API 지원
- GPU 메모리 관리
- 디스플레이 출력 관리

**비유:**
- GPU를 자동차라고 하면, NVIDIA 드라이버는 **"운전면허증"**
- 이것이 없으면 GPU를 아예 사용할 수 없음

**설치 시점:**
- GPU를 처음 설치할 때 필수
- 게임, 영상 편집, 일반 사용에도 필요
- 정기적으로 업데이트 권장

**다운로드:**
```
https://www.nvidia.com/download/index.aspx
→ GPU 모델 선택 (예: GTX 960)
→ 최신 드라이버 다운로드 및 설치
```

---

### 🧰 CUDA Toolkit

**역할:**
- NVIDIA GPU에서 **병렬 연산(딥러닝, 과학계산)**을 수행하기 위한 **개발 도구 모음**
- 일반 그래픽 작업이 아닌, GPU를 "계산기"로 사용하기 위한 전문 도구

**구성요소:**
- **CUDA 런타임 라이브러리**: GPU 병렬 연산 실행 환경
- **CUDA 컴파일러(nvcc)**: GPU 프로그램 개발용
- **개발 도구**: 디버거, 프로파일러 등
- **샘플 코드**: CUDA 프로그래밍 예제

**기능:**
- GPU 병렬 연산 API 제공
- 딥러닝 프레임워크(PyTorch, TensorFlow)가 GPU를 활용하도록 지원
- 과학 계산, 데이터 분석에 GPU 사용 가능

**비유:**
- NVIDIA 드라이버가 "운전면허증"이라면, CUDA Toolkit은 **"특수 작업용 도구"**
- 일반 운전(그래픽)에는 불필요하지만, 특수 작업(딥러닝)에는 필수

**설치 시점:**
- 딥러닝, 과학계산 등 GPU 병렬 연산이 필요할 때만
- 게임, 영상 편집에는 불필요

**다운로드:**
```
https://developer.nvidia.com/cuda-toolkit-archive
→ CUDA Toolkit 11.x 버전 선택 (프로젝트에서는 11.8 권장)
→ Windows용 다운로드 및 설치
```

---

### 🔗 의존성 관계

```
[하드웨어]
NVIDIA GPU (GTX 960)
    ↓
[1단계: 운영체제 인식]
NVIDIA 드라이버
    ↓
[2단계: 병렬 연산 지원]
CUDA Toolkit (개발 도구)
    ↓
[3단계: Python 인터페이스]
onnxruntime-gpu (Python 패키지)
    ↓
[4단계: 딥러닝 라이브러리]
InsightFace (얼굴 감지)
```

**각 단계 설명:**
1. **NVIDIA 드라이버**: GPU를 컴퓨터가 인식하고 사용할 수 있게 함
2. **CUDA Toolkit**: GPU로 병렬 연산을 할 수 있는 기반 제공
3. **onnxruntime-gpu**: Python에서 CUDA를 쉽게 사용하도록 연결
4. **InsightFace**: 실제 얼굴 감지 기능 제공

---

### 🎯 본 프로젝트에서의 활용

#### Python 소스 실행 시
```
[필수 설치 순서]
1. NVIDIA 드라이버 설치
2. CUDA Toolkit 11.x 설치
3. pip install onnxruntime-gpu
4. pip install insightface

[동작 과정]
onnxruntime-gpu가 시스템의 CUDA Toolkit을 찾아서 GPU 사용
```

#### EXE 실행 시 (PyInstaller 빌드)
```
[필수 설치]
1. NVIDIA 드라이버만 설치 ✅

[불필요한 설치]
2. CUDA Toolkit ❌ (EXE에 포함됨)
3. Python 패키지 ❌ (EXE에 포함됨)

[동작 과정]
PyInstaller가 onnxruntime-gpu의 CUDA 런타임 DLL을 함께 번들링
→ dist/출결관리/_internal/onnxruntime/ 폴더에 CUDA 관련 DLL 포함
→ NVIDIA 드라이버만 있으면 GPU 사용 가능
```

**핵심 차이:**
- **Python 소스**: CUDA Toolkit을 시스템에서 찾아서 사용 (별도 설치 필요)
- **EXE**: CUDA 런타임을 EXE 안에 포함 (별도 설치 불필요)

---

### 🔍 실제 파일 위치 확인

#### Python 소스 실행 시
```
# CUDA Toolkit 설치 경로 (Windows)
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\
├─ bin/
│  ├─ cudart64_110.dll     # CUDA 런타임
│  ├─ cublas64_11.dll      # CUDA 행렬 연산
│  └─ ...
└─ lib/

# onnxruntime-gpu가 위 경로의 DLL을 찾아서 사용
```

#### EXE 실행 시
```
# PyInstaller 빌드 결과
dist/출결관리/_internal/onnxruntime/
├─ onnxruntime_providers_cuda.dll
├─ cudart64_110.dll        # CUDA 런타임 (번들링됨!)
├─ cublas64_11.dll         # CUDA 행렬 연산 (번들링됨!)
└─ ...

# CUDA Toolkit 설치 없이도 위 DLL로 GPU 사용 가능
```

---
