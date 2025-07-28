#!/usr/bin/env python3
"""
Launcher script for NextCare2 application
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    sys.exit(main())