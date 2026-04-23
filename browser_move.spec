# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from pathlib import Path
import os

block_cipher = None

# Project root - use SPECPATH which PyInstaller provides
root = Path(SPECPATH) if 'SPECPATH' in dir() else Path(os.path.dirname(os.path.abspath(__file__))) if '__file__' in dir() else Path('.')

a = Analysis(
    ['src/browser_move/main.py'],
    pathex=[str(root)],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'pystray',
        'winshell',
        'screeninfo',
        'win32gui',
        'win32con',
        'win32event',
        'win32com.client',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='browser_move',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='browser_move',
)
