# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# ==================== 데이터 및 바이너리 수집 ====================

import os

datas = []
binaries = []
hiddenimports = []

# InsightFace 모델 파일 추가
insightface_models_src = os.path.join(os.path.expanduser('~'), '.insightface', 'models', 'buffalo_l')
if os.path.exists(insightface_models_src):
    datas.append((insightface_models_src, '.insightface/models/buffalo_l'))

# onnxruntime 수집 (GPU/CPU 자동 감지, CUDA 런타임 포함)
onnx_datas, onnx_binaries, onnx_hiddenimports = collect_all('onnxruntime')
datas += onnx_datas
binaries += onnx_binaries
hiddenimports += onnx_hiddenimports

# insightface 수집
insight_datas, insight_binaries, insight_hiddenimports = collect_all('insightface')
datas += insight_datas
binaries += insight_binaries
hiddenimports += insight_hiddenimports

# 기타 패키지 수집
for pkg in ['mss', 'PIL', 'numpy', 'cv2']:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception:
        pass

# ==================== Hidden Imports 추가 ====================

hiddenimports += [
    # 프로젝트 내부 패키지
    'gui',
    'gui.main_window',
    'gui.dialogs',
    'features',
    'features.capture',
    'features.face_detection',
    'features.file_manager',
    'features.logger',
    'features.scheduler',
    'features.exceptions',
    'utils',
    'utils.config',
    'utils.monitor',
    # tkinter
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    # 내장 모듈
    'logging',
    'logging.handlers',
    'pathlib',
    'json',
    'csv',
    'datetime',
    # InsightFace
    'insightface.app',
    'insightface.model_zoo',
    'insightface.utils',
    # ONNX Runtime
    'onnxruntime.capi',
    'onnxruntime.capi.onnxruntime_pybind11_state',
    # NumPy
    'numpy.core._multiarray_umath',
    # mss
    'mss.windows',
    # Pillow
    'PIL.Image',
    'PIL.ImageDraw',
    # jaraco and backports dependencies
    'jaraco.context',
    'backports.tarfile',
]

# ==================== Analysis ====================

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ==================== PYZ ====================

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ==================== EXE (--onedir) ====================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # --onedir용 설정
    name='출결관리',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # UPX 압축 활성화
    console=False,  # GUI 모드 (콘솔 창 숨김)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ==================== COLLECT (--onedir) ====================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='출결관리',
)
