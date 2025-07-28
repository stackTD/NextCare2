#!/usr/bin/env python3
"""
Standalone script to run the Mock PLC simulator
"""

import sys
import os
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mock_sensor.mock_plc import run_mock_plc

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Starting NextCare2 Mock PLC Simulator...")
    print("Server will listen on localhost:8888")
    print("Press Ctrl+C to stop")
    
    try:
        run_mock_plc()
    except KeyboardInterrupt:
        print("\nMock PLC simulator stopped.")
    except Exception as e:
        print(f"Error running mock PLC: {e}")
        sys.exit(1)