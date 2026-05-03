# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Human-like Typer (includes hltyper package + pynput Win32)."""

import os
from pathlib import Path

# PyInstaller injects SPECPATH when running the spec; fall back to CWD.
try:
    spec_dir = str(Path(SPECPATH).resolve().parent)
except NameError:
    spec_dir = os.getcwd()

from PyInstaller.utils.hooks import collect_submodules

hltyper_submods = collect_submodules("hltyper")

a = Analysis(
    ["human_like_typer.py"],
    pathex=[spec_dir],
    binaries=[],
    datas=[],
    hiddenimports=hltyper_submods
    + [
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
    ],
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
    name="human_like_typer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
