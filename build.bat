@echo off
chcp 65001 > nul
echo ========================================
echo 출결관리 EXE 빌드 스크립트
echo ========================================
echo.

REM 가상환경 활성화 확인
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] PyInstaller를 찾을 수 없습니다.
    echo 가상환경이 활성화되어 있는지 확인하세요.
    echo.
    echo 활성화 방법:
    echo   conda activate capture
    echo   또는
    echo   venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo [1/3] 기존 빌드 삭제 중...
if exist build (
    rmdir /s /q build
    echo   - build 폴더 삭제 완료
)
if exist dist (
    rmdir /s /q dist
    echo   - dist 폴더 삭제 완료
)
echo.

echo [2/3] EXE 빌드 중... (2~3분 소요)
pyinstaller 출결관리.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo [오류] 빌드 실패
    pause
    exit /b 1
)
echo.

echo [3/3] 빌드 완료!
echo.
echo ========================================
echo EXE 위치: dist\출결관리\출결관리.exe
echo ========================================
echo.
echo 실행 방법:
echo   cd dist\출결관리
echo   .\출결관리.exe
echo.
pause
