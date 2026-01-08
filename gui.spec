# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Huffman Compressor GUI
Builds a single-file executable with all dependencies bundled
"""

import sys
from pathlib import Path

block_cipher = None

# Get the base directory
base_dir = Path('.').absolute()

a = Analysis(
    ['gui.py'],
    pathex=[str(base_dir)],
    binaries=[
        # Include the huffman.exe backend
        ('huffman.exe', '.'),
    ],
    datas=[
        # Include the gui package
        ('gui', 'gui'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HuffmanCompressor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)
