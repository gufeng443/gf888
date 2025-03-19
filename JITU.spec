# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:/GP/pythonProject1/pages/JITU.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['threading', 'os', 'PIL', 'tkinter', 'pytesseract', 're', 'concurrent.futures', 'time', 'subprocess'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='JITU',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
