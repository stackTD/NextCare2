# Building NextCare2 Executable

This guide provides step-by-step instructions for creating a standalone executable (.exe) file for the NextCare2 application using PyInstaller.

## Overview

The NextCare2 application can be packaged into a standalone executable that includes all dependencies, allowing distribution without requiring users to install Python or any dependencies.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: At least 4GB RAM (8GB recommended for build process)
- **Disk Space**: At least 2GB free space for build artifacts

### Required Software

1. **Python 3.8+** with pip
2. **Git** (if cloning from repository)
3. **Visual C++ Redistributable** (Windows only, usually pre-installed)

## Installation

### 1. Clone or Download the Repository

```bash
# Clone from repository
git clone https://github.com/stackTD/NextCare2.git
cd NextCare2

# Or download and extract the ZIP file
```

### 2. Verify Python Installation

```bash
python --version
# Should show Python 3.8.0 or higher

pip --version
# Should show pip version
```

### 3. Install Project Dependencies

The build script will automatically install dependencies, but you can also install them manually:

```bash
pip install -r requirements.txt
```

## Building the Executable

### Option 1: Automated Build (Recommended)

Use the provided build script for a fully automated process:

```bash
# Basic build
python build_exe.py

# Clean build (removes previous build artifacts)
python build_exe.py --clean

# Build without console window (Windows only)
python build_exe.py --no-console

# Verbose output for debugging
python build_exe.py --verbose

# Combined options
python build_exe.py --clean --verbose
```

### Option 2: Manual Build with PyInstaller

If you prefer manual control over the build process:

```bash
# Install PyInstaller
pip install pyinstaller

# Build using the spec file
pyinstaller nextcare.spec

# Or build directly from script
pyinstaller --onefile --name NextCare2 run_nextcare.py
```

## Build Configuration

### PyInstaller Spec File (`nextcare.spec`)

The spec file contains the complete build configuration:

- **Entry Point**: `run_nextcare.py`
- **Application Name**: NextCare2
- **Build Mode**: Single file (`--onefile`)
- **Console Mode**: Enabled by default (can be disabled)
- **Data Files**: Includes `Images/` directory
- **Hidden Imports**: All required PyQt6, matplotlib, and database modules

### Customizing the Build

#### Changing Application Metadata

Edit `nextcare.spec` to modify:

```python
app_name = 'NextCare2'           # Change application name
app_version = '1.0.0'            # Update version
app_description = 'Your Description'  # Modify description
```

#### Adding an Icon

1. Place your icon file (`.ico` for Windows, `.icns` for macOS) in the project directory
2. Update the spec file:

```python
icon='your_icon.ico',  # Add icon path
```

#### Window vs Console Mode

For a windowed application without console:

```python
console=False,  # Disable console window
```

#### Directory vs Single File Distribution

For directory distribution (faster startup):

Uncomment the `COLLECT` section in `nextcare.spec`:

```python
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
```

## Build Output

### Generated Files

After a successful build, you'll find:

```
dist/
├── NextCare2.exe          # Main executable (Windows)
├── NextCare2              # Main executable (Linux/macOS)
└── [other files]          # Additional files (directory mode only)

build/                     # Temporary build files (can be deleted)
├── NextCare2/
└── [build artifacts]
```

### File Sizes

Typical executable sizes:
- **Single file**: 150-300MB (includes all dependencies)
- **Directory mode**: 200-400MB total (faster startup)

## Testing the Executable

### Basic Testing

1. **Navigate to the dist directory**:
   ```bash
   cd dist
   ```

2. **Run the executable**:
   ```bash
   # Windows
   NextCare2.exe

   # Linux/macOS
   ./NextCare2
   ```

3. **Verify functionality**:
   - Application starts without errors
   - UI loads correctly
   - All features work as expected

### Advanced Testing

1. **Test on clean system** without Python installed
2. **Test different Windows versions** (if targeting Windows)
3. **Verify database connections** work properly
4. **Check all UI components** and features

## Distribution

### Preparing for Distribution

1. **Test thoroughly** on target systems
2. **Create installation package** (optional):
   - Use NSIS (Windows)
   - Use DMG (macOS)
   - Use AppImage or DEB (Linux)

3. **Document system requirements** for end users
4. **Provide troubleshooting guide**

### Distribution Checklist

- [ ] Executable tested on clean system
- [ ] All dependencies included
- [ ] Application starts correctly
- [ ] Features work as expected
- [ ] Documentation provided
- [ ] Support contact information included

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Solution**: Add missing modules to `hiddenimports` in `nextcare.spec`:

```python
hiddenimports = [
    'your_missing_module',
    # ... other modules
]
```

#### 2. PyQt6 import errors

**Solution**: Ensure PyQt6 is properly installed:

```bash
pip install --upgrade PyQt6
```

#### 3. Matplotlib backend issues

**Solution**: The spec file includes matplotlib backends. If issues persist:

```python
hiddenimports = [
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_agg',
    # ... other backends
]
```

#### 4. Large executable size

**Solutions**:
- Use directory mode instead of single file
- Exclude unnecessary modules in spec file
- Use UPX compression (already enabled)

#### 5. Slow startup time

**Solutions**:
- Use directory mode distribution
- Reduce number of hidden imports
- Optimize application startup code

#### 6. Antivirus false positives

**Solutions**:
- Submit executable to antivirus vendors for analysis
- Sign the executable with a code signing certificate
- Provide hash checksums for verification

### Debug Mode

For debugging build issues:

```bash
# Enable debug mode
python build_exe.py --verbose

# Or with PyInstaller directly
pyinstaller --log-level=DEBUG nextcare.spec
```

### Getting Help

1. **Check PyInstaller documentation**: https://pyinstaller.readthedocs.io/
2. **Review build logs** for specific error messages
3. **Test with minimal example** to isolate issues
4. **Check for known issues** with specific modules

## Performance Optimization

### Reducing Executable Size

1. **Exclude unnecessary modules**:
   ```python
   excludes=[
       'tkinter',
       'test',
       'unittest',
       'distutils',
   ]
   ```

2. **Use directory mode** for larger applications
3. **Enable UPX compression** (already enabled in spec)

### Improving Startup Time

1. **Use directory mode** instead of single file
2. **Minimize hidden imports** to only required modules
3. **Optimize application initialization** code

## Security Considerations

### Code Signing (Recommended)

For production distribution:

1. **Obtain code signing certificate**
2. **Sign the executable**:
   ```bash
   signtool sign /f certificate.pfx /p password NextCare2.exe
   ```

### Best Practices

- **Use HTTPS** for download distribution
- **Provide checksums** for integrity verification
- **Keep build environment** secure and up-to-date
- **Regularly update dependencies** for security patches

## Advanced Configuration

### Custom Hooks

Create custom PyInstaller hooks for complex dependencies:

```python
# hooks/hook-mymodule.py
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('mymodule')
```

### Runtime Hooks

Add runtime hooks for initialization:

```python
runtime_hooks=['runtime_hook.py']
```

### Version Information (Windows)

Create `file_version_info.txt` for Windows version info:

```python
version='file_version_info.txt'
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build Executable

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Build executable
      run: python build_exe.py --clean
    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: NextCare2-executable
        path: dist/
```

## Support

For additional help or issues:

1. **Review this documentation** thoroughly
2. **Check the project repository** for updates
3. **Review PyInstaller documentation** for advanced topics
4. **Contact the development team** for specific issues

---

**Note**: This guide assumes familiarity with command-line operations. Adjust paths and commands according to your operating system and environment.