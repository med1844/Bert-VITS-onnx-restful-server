# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

datas = []
for package in [
    "tqdm",
    "regex",
    "requests",
    "packaging",
    "filelock",
    "numpy",
    "tokenizers",
    "huggingface-hub",
    "safetensors",
    "accelerate",
    "pyyaml",
    "sentencepiece",
    "torch",
]:
    datas.extend(copy_metadata(package))
datas.extend(
    [
        (".venv_windows/Lib/site-packages/jieba/dict.txt", "jieba"),
        (".venv_windows/Lib/site-packages/g2p_en/homographs.en", "g2p_en"),
        (".venv_windows/Lib/site-packages/g2p_en/checkpoint20.npz", "g2p_en"),
        (".venv_windows/Lib/site-packages/transformers/models/deberta_v2/modeling_deberta_v2.py", "transformers/models/deberta_v2"),
        ("./commons.py", "."),
        ("./text/cmudict.rep", "text"),
        ("./text/cmudict_cache.pickle", "text"),
        ("./text/opencpop-strict.txt", "text"),
    ]
)

import sys

sys.setrecursionlimit(sys.getrecursionlimit() * 50)


block_cipher = None


a = Analysis(
    ["server.py"],
    pathex=[".venv_windows/Lib/site-packages"],
    binaries=[],
    datas=datas,
    hiddenimports=["tqdm", "sentencepiece"],
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
    name="server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="server",
)
