# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for NextCare2 application.
This file defines the configuration for building a standalone executable.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Application metadata
app_name = 'NextCare2'
app_version = '1.0.0'
app_description = 'Predictive Maintenance System'

# Paths
current_dir = os.path.dirname(os.path.abspath(SPEC))
src_dir = os.path.join(current_dir, 'src')
images_dir = os.path.join(current_dir, 'Images')

# Add src directory to Python path
sys.path.insert(0, src_dir)

# Collect data files
datas = []

# Add Images directory
if os.path.exists(images_dir):
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.ico', '.svg')):
            datas.append((os.path.join(images_dir, file), 'Images'))

# Collect matplotlib data files
datas += collect_data_files('matplotlib')

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    
    # Matplotlib backends
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_agg',
    'matplotlib.figure',
    'matplotlib.pyplot',
    'matplotlib.dates',
    
    # Database modules
    'psycopg2',
    'psycopg2.extras',
    'psycopg2.extensions',
    
    # Other dependencies
    'bcrypt',
    'numpy',
    'pandas',
    'dotenv',
    
    # Collect all submodules from src directory
] + collect_submodules('src')

# Analysis configuration
a = Analysis(
    ['run_nextcare.py'],
    pathex=[current_dir, src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'test',
        'unittest',
        'distutils',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for windowed mode, True for console output during development
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',  # Optional: add version info file
    icon=None,  # Optional: add icon file path here
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following lines if you prefer directory distribution
"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
"""