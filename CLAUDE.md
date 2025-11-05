# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Attendance Management Auto-Capture System**

An automated screenshot capture system for online class (Zoom) attendance verification using face detection with InsightFace.

- **Environment**: Windows 10, Python 3.10.11, Dual Monitor, NVIDIA GTX 960
- **Purpose**: Automatically capture Zoom gallery view screenshots when attendance threshold is met
- **Key Features**: Face detection (InsightFace), scheduled capture by class period, dual monitor support

## Development Environment

**Python Version**: 3.10.11 (Fixed - Do not change)

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

**Run the Application**:
```bash
# Make sure you're in the project root directory
python main.py
```

**Key Dependencies**:
- `insightface==0.7.3` - Face detection
- `onnxruntime-gpu==1.16.3` - GPU acceleration (requires CUDA 11.x)
- `mss==9.0.1` - Screen capture
- `Pillow==10.1.0` - Image processing
- `numpy==1.24.3` - Array processing
- `tkinter` - GUI (Python built-in)

## Architecture

**Application Entry Point**:
- `main.py` is the entry point (currently a placeholder stub)
- **Startup Flow** (not yet implemented):
  1. `main.py` launches → shows `InitDialog` (from `gui/dialogs.py`)
  2. User configures: monitor selection, save path, capture mode, student count
  3. `InitDialog` returns configuration dict
  4. `MainWindow` (from `gui/main_window.py`) launches with configuration
  5. `MainWindow` initializes all feature modules (ScreenCapture, FaceDetector, etc.)
  6. `Scheduler` starts, waits for scheduled capture times
  7. Application runs until user closes window

**MVC-like Pattern**:
```
capture/
├─ main.py       # Entry point (launches InitDialog → MainWindow)
├─ features/     # Core business logic (Model + Controller)
│  ├─ capture.py          # Screen capture (ScreenCapture class)
│  ├─ face_detection.py   # Face detection (FaceDetector class with InsightFace)
│  ├─ file_manager.py     # File saving (FileManager class)
│  ├─ logger.py           # CSV logging (CSVLogger class)
│  └─ scheduler.py        # Scheduling (CaptureScheduler class)
├─ gui/          # View layer
│  ├─ main_window.py      # Main window (MainWindow class)
│  └─ dialogs.py          # Initial setup dialog (InitDialog class)
└─ utils/        # Utilities
   ├─ config.py           # Configuration management (Config class)
   └─ monitor.py          # Monitor detection (utility functions)
```

**Key Design Principles**:
- Loose coupling between layers
- Each module independently testable
- Unidirectional data flow (GUI → Features → External Libraries)
- Single responsibility per class

## Core Workflow

**Data Flow Architecture**:
```
InitDialog (startup)
    ↓ (returns config dict)
MainWindow launches
    ↓ (initializes all modules)
Scheduler starts
    ↓ (waits for scheduled time)
Scheduler triggers capture callback
    ↓
ScreenCapture.capture() → Image (numpy array)
    ↓
FaceDetector.detect(image) → Face count (int)
    ↓
Compare with threshold
    ↓ (if threshold met)
FileManager.save_image(is_within_window) → File path
    ↓
CSVLogger.log_event() → CSV entry
    ↓
MainWindow.update_period_status() → UI update
    ↓
MainWindow.show_alert() → Success notification
```

**Capture Process Details**:
1. **Scheduler triggers** at scheduled time (e.g., 09:30 for period 1)
2. **ScreenCapture** captures selected monitor → image in memory
3. **FaceDetector** detects faces in captured image using GPU (GTX 960)
4. **Compare** face count with threshold (student count + 1 teacher)
5. **If threshold met**:
   - Save image (already captured) to file
   - Log event to CSV
   - Show success alert
   - Stop detection for this period
6. **If failed**:
   - Discard image
   - Wait 10 seconds
   - Retry from step 2 (only if still within capture window)

**CRITICAL**: Do NOT re-capture after detection. The image captured in step 2 is saved in step 5 if conditions are met.

**Two Capture Modes**:
- **Exact Mode**: Detected count must exactly match threshold
  - Example: 22 detected = 22 threshold ✓ | 21 detected = 22 threshold ✗
- **Flexible Mode (Recommended)**: Detected count ≥ threshold × 0.9
  - Example: 20 detected ≥ 19.8 (22 × 0.9) ✓
  - Accounts for poor lighting, camera angles, low webcam quality
  - Default mode due to real-world student webcam environment variability

**State Management**:
- Configuration stored in `config.json` (via `utils/config.py`)
- Runtime state managed by `MainWindow` class
- Each period has independent state: 대기중 → 감지중 → 완료 | 건너뛰기 | 시간 초과

## Coding Standards

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

**CRITICAL: NO AI Attribution**:
- ❌ NEVER include "Generated with Claude Code" or similar AI tool signatures
- ❌ NEVER add "Co-Authored-By: Claude" or similar AI credits
- ✅ Only suggest what the user requested, nothing more

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
6. If met: Save the already-captured image with `is_within_window` parameter
   - Within capture window: Overwrite existing file
   - After capture window: Save as `_수정.png`
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

When making changes, always consult these documents:
- `docs/requirements.md` - Complete requirements specification (what to build)
- `docs/architecture.md` - Technical design and class structures (how to build)
- `docs/rules.md` - Detailed coding rules (how to write code - MUST follow)
- `docs/tasks.md` - Development task checklist and progress tracking

**Note**: The `.cursorrules` file has been removed and replaced by this CLAUDE.md file.

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
- Model provides 95-99% accuracy, far superior to Haar Cascade (60-70%)

**Dual Monitor Context**:
- School computer has 2 monitors
- Zoom typically on secondary monitor
- Must capture entire monitor including Windows taskbar (for timestamp proof)
- User selects monitor via InitDialog at startup

**Student Count Logic**:
- Input: Student count (excluding teacher)
- Threshold: Student count + 1 (teacher)
- Example: 21 students → Threshold 22 people
- Flexible mode: Threshold × 0.9 = 19.8 → 20 people minimum

**Class Schedule** (8 periods + checkout):
- Period 1-8: Capture window is minutes 30-45 of period start hour
  - Period 1 (09:30 start) → Capture 09:30-09:45
  - Period 2 (10:30 start) → Capture 10:30-10:45
  - ... (continues for all 8 periods)
- Checkout: 18:30-18:32 (2-minute window)
- Lunch break (13:30-14:30): No capture
- Retry interval: Every 10 seconds within capture window

**File Naming Rules** (controlled by `is_within_window` parameter):
- Within capture window retry (`is_within_window=True`): Overwrite existing file
  - `251020_1교시.png` → `251020_1교시.png` (overwrite)
- After capture window retry (`is_within_window=False`): Save as modified
  - `251020_1교시.png` (exists) → `251020_1교시_수정.png` (new file)
- This preserves original capture while allowing manual corrections
- The `is_within_window` parameter is determined by `Scheduler.is_in_capture_window()`

## Development Progress Tracking

For current development status and task progress, see `docs/tasks.md`.

When implementing new features, follow the specifications in `docs/architecture.md` for class structures and `docs/rules.md` for coding standards.

---

**Document Version**: 2.1
**Last Updated**: 2025-11-05
**Major Changes**:
- Updated Core Workflow: `update_status()` → `update_period_status()`
- Updated Data Flow: Added `is_within_window` parameter to `FileManager.save_image()`
- Updated Face Detection Flow: Added file naming logic based on capture window
- Updated File Naming Rules: Added `is_within_window` parameter explanation
- Synchronized with architecture.md v2.0 changes
