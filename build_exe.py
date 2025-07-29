#!/usr/bin/env python3
"""
Automated build script for NextCare2 executable generation using PyInstaller.
This script handles the complete build process including dependency installation
and error handling.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

class NextCareBuildError(Exception):
    """Custom exception for build errors"""
    pass

class NextCareBuilder:
    """Main builder class for NextCare2 executable generation"""
    
    def __init__(self, clean_build=False, console_mode=True, verbose=False):
        self.project_root = Path(__file__).parent.absolute()
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        self.spec_file = self.project_root / 'nextcare.spec'
        self.clean_build = clean_build
        self.console_mode = console_mode
        self.verbose = verbose
        
    def log(self, message, level="INFO"):
        """Log a message with optional level"""
        if level == "ERROR":
            print(f"❌ {message}", file=sys.stderr)
        elif level == "SUCCESS":
            print(f"✅ {message}")
        elif level == "WARNING":
            print(f"⚠️  {message}")
        else:
            print(f"ℹ️  {message}")
    
    def run_command(self, command, description):
        """Run a shell command with error handling"""
        self.log(f"{description}...")
        
        if self.verbose:
            self.log(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=not self.verbose,
                text=True,
                cwd=self.project_root
            )
            
            if not self.verbose and result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
                
            return result
            
        except subprocess.CalledProcessError as e:
            error_msg = f"{description} failed"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            elif e.stdout:
                error_msg += f": {e.stdout.strip()}"
            raise NextCareBuildError(error_msg)
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        self.log("Checking Python version")
        
        if sys.version_info < (3, 8):
            raise NextCareBuildError(
                f"Python 3.8+ required, but {sys.version} is installed"
            )
        
        self.log(f"Python version {sys.version} is compatible", "SUCCESS")
    
    def install_pyinstaller(self):
        """Install PyInstaller if not available"""
        try:
            import PyInstaller
            self.log(f"PyInstaller {PyInstaller.__version__} is already installed", "SUCCESS")
            return
        except ImportError:
            pass
        
        self.log("PyInstaller not found, installing...")
        self.run_command(
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
            "Installing PyInstaller"
        )
        self.log("PyInstaller installed successfully", "SUCCESS")
    
    def install_dependencies(self):
        """Install project dependencies"""
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            self.log("No requirements.txt found, skipping dependency installation", "WARNING")
            return
        
        self.log("Installing project dependencies")
        self.run_command(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            "Installing dependencies from requirements.txt"
        )
        self.log("Dependencies installed successfully", "SUCCESS")
    
    def clean_build_directories(self):
        """Clean previous build artifacts"""
        if not self.clean_build:
            return
        
        self.log("Cleaning previous build artifacts")
        
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                self.log(f"Removing {directory}")
                shutil.rmtree(directory)
        
        self.log("Build directories cleaned", "SUCCESS")
    
    def validate_source_files(self):
        """Validate that required source files exist"""
        self.log("Validating source files")
        
        required_files = [
            'run_nextcare.py',
            'src/main.py',
            'requirements.txt'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            raise NextCareBuildError(
                f"Missing required files: {', '.join(missing_files)}"
            )
        
        self.log("All required source files found", "SUCCESS")
    
    def update_spec_file(self):
        """Update spec file for console mode if needed"""
        if not self.console_mode:
            return
        
        self.log("Updating spec file for console mode")
        
        # Read the spec file
        spec_content = self.spec_file.read_text()
        
        # Update console mode setting
        updated_content = spec_content.replace(
            'console=True,',
            f'console={self.console_mode},'
        )
        
        # Write back if changed
        if updated_content != spec_content:
            self.spec_file.write_text(updated_content)
            self.log("Spec file updated for console mode")
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        if not self.spec_file.exists():
            raise NextCareBuildError(f"Spec file not found: {self.spec_file}")
        
        self.log("Building executable with PyInstaller")
        
        # Build command
        cmd = [sys.executable, '-m', 'PyInstaller']
        
        if self.clean_build:
            cmd.append('--clean')
        
        if self.verbose:
            cmd.append('--log-level=DEBUG')
        
        cmd.append(str(self.spec_file))
        
        self.run_command(cmd, "Building executable")
        self.log("Executable built successfully", "SUCCESS")
    
    def verify_executable(self):
        """Verify that the executable was created successfully"""
        self.log("Verifying executable")
        
        # Look for the executable in dist directory
        exe_name = "NextCare2.exe" if sys.platform == "win32" else "NextCare2"
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            # Try without extension
            exe_path = self.dist_dir / "NextCare2"
            
        if not exe_path.exists():
            raise NextCareBuildError(f"Executable not found in {self.dist_dir}")
        
        # Check file size (should be reasonable)
        file_size = exe_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        if size_mb < 10:  # Suspiciously small
            self.log(f"Warning: Executable size is only {size_mb:.1f}MB", "WARNING")
        else:
            self.log(f"Executable created: {exe_path} ({size_mb:.1f}MB)", "SUCCESS")
        
        return exe_path
    
    def show_distribution_info(self, exe_path):
        """Show information about distributing the executable"""
        self.log("\n" + "="*50)
        self.log("BUILD COMPLETED SUCCESSFULLY", "SUCCESS")
        self.log("="*50)
        self.log(f"Executable location: {exe_path}")
        self.log(f"File size: {exe_path.stat().st_size / (1024*1024):.1f}MB")
        self.log("\nDistribution Notes:")
        self.log("• The executable is self-contained and includes all dependencies")
        self.log("• No Python installation required on target systems")
        self.log("• Distribute the entire 'dist' directory contents if using directory mode")
        self.log("• Test the executable on target systems before distribution")
        self.log("• Consider antivirus software may flag the executable (false positive)")
    
    def build(self):
        """Main build process"""
        try:
            self.log("Starting NextCare2 executable build process")
            self.log(f"Project root: {self.project_root}")
            
            # Pre-build checks
            self.check_python_version()
            self.validate_source_files()
            self.clean_build_directories()
            
            # Install dependencies
            self.install_dependencies()
            self.install_pyinstaller()
            
            # Build process
            self.update_spec_file()
            self.build_executable()
            
            # Post-build verification
            exe_path = self.verify_executable()
            self.show_distribution_info(exe_path)
            
            return exe_path
            
        except NextCareBuildError as e:
            self.log(f"Build failed: {e}", "ERROR")
            sys.exit(1)
        except KeyboardInterrupt:
            self.log("Build cancelled by user", "WARNING")
            sys.exit(1)
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Build NextCare2 executable using PyInstaller"
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build directories before building'
    )
    
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='Build without console window (Windows only)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create builder and run
    builder = NextCareBuilder(
        clean_build=args.clean,
        console_mode=not args.no_console,
        verbose=args.verbose
    )
    
    builder.build()

if __name__ == "__main__":
    main()