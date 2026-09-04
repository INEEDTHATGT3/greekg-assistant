# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/default_config.json', 'config'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'customtkinter',
        'pystray',
        'PIL',
        'PIL._tkinter_finder',
        'numpy',
        'sounddevice',
        'soundfile',
        'pyperclip',
        'keyboard',
        'requests',
        'faster_whisper',
        'docx',
        'openwakeword',
        'openwakeword.model',
        'core',
        'core.audio',
        'core.whisper_local',
        'core.whisper_api',
        'core.ai_ollama',
        'core.ai_api',
        'core.wake_word',
        'core.app_launcher',
        'core.docx_export',
        'core.clipboard',
        'gui',
        'gui.app',
        'gui.tray',
        'gui.dictate_tab',
        'gui.launch_tab',
        'gui.savetodocx_tab',
        'gui.settings_tab',
        'gui.widgets',
        'config',
        'config.settings',
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
    name='GreekG Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GreekG Assistant',
)
