# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Attendance Management Auto-Capture System**

An automated screenshot capture system for online class (Zoom) attendance verification using face detection with InsightFace.

- **Environment**: Windows 10, Python 3.10.11, Dual Monitor, NVIDIA GTX 960
- **Purpose**: Automatically capture Zoom gallery view screenshots when attendance threshold is met
- **Key Features**: Face detection (InsightFace), scheduled capture by class period, dual monitor support

## Development Environment

**Python Version**: 3.10.11 (Fixed)

**Virtual Environment Setup**:
```bash
# Using conda (recommended)
conda create -n capture python=3.10.11
conda activate capture
pip install -r requirements.txt

# Using venv
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Key Dependencies**:
- `insightface==0.7.3` - Face detection
- `onnxruntime-gpu==1.16.3` - GPU acceleration
- `mss==9.0.1` - Screen capture
- `Pillow==10.1.0` - Image processing
- `numpy==1.24.3` - Array processing
- `tkinter` - GUI (built-in)

## Architecture

**MVC-like Pattern**:
```
capture/
├─ features/     # Core business logic (Model + Controller)
│  ├─ capture.py          # Screen capture
│  ├─ face_detection.py   # Face detection (InsightFace)
│  ├─ file_manager.py     # File saving
│  ├─ logger.py           # CSV logging
│  └─ scheduler.py        # Scheduling
├─ gui/          # View layer
│  ├─ main_window.py      # Main window
│  └─ dialogs.py          # Initial setup dialog
└─ utils/        # Utilities
   ├─ config.py           # Configuration management
   └─ monitor.py          # Monitor detection
```

**Key Design Principles**:
- Loose coupling between layers
- Each module independently testable
- Unidirectional data flow
- Single responsibility per class

## Core Workflow

**Capture Process**:
1. Scheduler triggers at scheduled time
2. ScreenCapture captures selected monitor
3. FaceDetector detects faces in captured image using GPU
4. Compare face count with threshold (student count + 1 teacher)
5. If threshold met: Save image, log to CSV, show success alert
6. If failed: Wait 10 seconds, retry until time window ends

**Two Capture Modes**:
- **Exact Mode**: Detected count must exactly match threshold
- **Flexible Mode (Recommended)**: Detected count ≥ threshold × 0.9
  - Accounts for poor lighting, camera angles, low webcam quality
  - Default mode due to real-world student webcam environment variability

## Coding Standards (from .cursorrules)

**Naming Conventions**:
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Methods: `snake_case` (start with verb)
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Code Constraints**:
- Function length: Max 50 lines
- Class length: Max 500 lines
- Line length: Max 120 characters
- If exceeds: Split into helper functions or separate classes

**Required Practices**:
- **Docstrings**: All classes and functions must have docstrings
- **Type Hints**: All function signatures must include type hints
- **Error Handling**: All external calls must use try-except with `logger.error()`
- **Import Order**: 1) Standard library, 2) External libraries, 3) Internal modules

**File I/O**:
- Use `pathlib.Path` (not string concatenation)
- Use `with` statement for file operations
- CSV files: UTF-8-BOM encoding (for Excel compatibility)

**Error Handling Pattern**:
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

## Git Workflow

**Branch Strategy**: GitHub Flow

```bash
# 1. Start new feature
git checkout -b feature/feature-name

# 2. Develop and test
git add specific_file.py
git commit -m "feat: implement feature"

# 3. Merge to main when complete
git checkout main
git merge feature/feature-name
git branch -d feature/feature-name
```

**Commit Message Format**:
```
<type>: <subject>

<body> (optional)
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Commit Principles** (Important for AI):
- AI suggests commit messages and commands only
- User reviews code and executes commit manually
- Separate commits per file when different features
- One commit = One feature/fix

## Testing Commands

**Run Tests** (when implemented):
```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_face_detection.py

# With coverage
python -m pytest --cov=features tests/
```

## Key Implementation Details

**Dual Monitor Handling**:
- User selects capture monitor in InitDialog at startup
- `utils/monitor.py` provides `get_monitor_names()` and `get_monitor_count()`
- ScreenCapture class uses mss library with monitor ID

**Face Detection Flow** (Critical Order):
1. Capture screen to memory (mss)
2. Load captured image into InsightFace
3. GPU-accelerated face detection (GTX 960)
4. Count detected faces
5. Compare with threshold
6. If met: Save the already-captured image (don't re-capture)
7. If failed: Discard image, wait 10 seconds, retry from step 1

**File Naming Convention**:
- Folder: `YYMMDD/` (e.g., `251020/`)
- Regular: `YYMMDD_N교시.png` (e.g., `251020_1교시.png`)
- Modified: `YYMMDD_N교시_수정.png` (when retrying after time window)
- Checkout: `YYMMDD_퇴실.png`
- Log: `YYMMDD_log.csv`

**Schedule Times**:
- Classes 1-8: Capture during minutes 30-45 of each hour starting time
  - Example: Class 1 (09:30 start) → Capture window 09:30-09:45
- Checkout: 18:30-18:32 (2-minute window)
- Retry interval: 10 seconds

## Important Reference Documents

When making changes, always consult:
- `docs/requirements.md` - Complete requirements specification
- `docs/rules.md` - Detailed coding rules (must follow)
- `docs/architecture.md` - Technical design and class structures
- `docs/tasks.md` - Task checklist
- `.cursorrules` - Quick reference for coding standards

## Performance Targets

- Screen capture: ≤ 0.5s
- Face detection (GPU): ≤ 0.5s
- File save: ≤ 0.5s
- **Total processing**: ≤ 2s

**Memory Management**:
- InsightFace model: ~500MB GPU memory
- Explicitly release with `cleanup()` method
- Delete large image objects after processing

## Common Development Patterns

**Adding New UI Section**:
1. Add UI variable in `__init__` (e.g., `self.some_var: Optional[tk.StringVar]`)
2. Create `_create_section_name(parent)` method (≤50 lines)
3. If complex, split into helper methods (e.g., `_create_input_area()`, `_create_display()`)
4. Group related methods under section comment (e.g., `# ==================== Section Name ====================`)
5. Update `on_ok()` to collect value
6. Add validation if needed

**Adding New Feature Module**:
1. Create file in `features/` folder
2. Define class with docstring
3. Implement with proper error handling
4. Add unit test in `tests/`
5. Update this CLAUDE.md if it changes architecture

## Special Notes

**InsightFace GPU Usage**:
- First run downloads ~100MB model to `~/.insightface/models/buffalo_l/`
- GPU context: `ctx_id=0` (for GTX 960)
- Fallback to CPU if GPU unavailable (show warning to user)

**Dual Monitor Context**:
- School computer has 2 monitors
- Zoom typically on secondary monitor
- Must capture entire monitor including Windows taskbar (for timestamp proof)

**Student Count Logic**:
- Input: Student count (excluding teacher)
- Threshold: Student count + 1 (teacher)
- Example: 21 students → Threshold 22 people
- Flexible mode: Threshold × 0.9 = 19.8 → 20 people minimum

---

**Document Version**: 1.0
**Last Updated**: 2025-10-29
