"""
NextCare Mock Sensor System

This module provides mock sensor functionality for testing and demonstration purposes.
It simulates real sensor data with realistic patterns, anomalies, and alert conditions.
"""

import random
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import json
import math


@dataclass
class SensorConfig:
    """Configuration for a mock sensor"""
    name: str
    unit: str
    min_value: float
    max_value: float
    normal_range: tuple[float, float]
    warning_threshold: float
    alarm_threshold: float
    noise_level: float = 0.05
    trend_probability: float = 0.1
    spike_probability: float = 0.02
    update_interval: int = 60  # seconds


@dataclass
class MockMachine:
    """Mock machine configuration"""
    machine_id: str
    name: str
    location: str
    sensors: Dict[str, SensorConfig] = field(default_factory=dict)
    is_active: bool = True
    failure_probability: float = 0.001


class SensorDataPoint:
    """Represents a single sensor reading"""
    
    def __init__(self, machine_id: str, parameter_id: str, value: float, 
                 timestamp: datetime = None, quality: float = 1.0):
        self.machine_id = machine_id
        self.parameter_id = parameter_id
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()
        self.quality = quality
        self.source = 'mock'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            'machine_id': self.machine_id,
            'parameter_id': self.parameter_id,
            'value': round(self.value, 3),
            'timestamp': self.timestamp.isoformat(),
            'quality': self.quality,
            'source': self.source
        }
    
    def __str__(self):
        return f"{self.machine_id}.{self.parameter_id}: {self.value:.3f} @ {self.timestamp}"


class MockSensor:
    """Individual mock sensor implementation"""
    
    def __init__(self, machine_id: str, parameter_id: str, config: SensorConfig):
        self.machine_id = machine_id
        self.parameter_id = parameter_id
        self.config = config
        self.current_value = random.uniform(*config.normal_range)
        self.trend_direction = 0  # -1, 0, 1 for down, stable, up
        self.trend_duration = 0
        self.last_reading_time = datetime.utcnow()
        self.logger = logging.getLogger(f"MockSensor.{machine_id}.{parameter_id}")
    
    def generate_reading(self) -> SensorDataPoint:
        """Generate the next sensor reading"""
        now = datetime.utcnow()
        
        # Calculate time since last reading
        time_delta = (now - self.last_reading_time).total_seconds()
        
        # Apply trend if active
        if self.trend_duration > 0:
            trend_change = self.trend_direction * 0.1 * (time_delta / 60)  # Change per minute
            self.current_value += trend_change
            self.trend_duration -= time_delta
        else:
            # Check for new trend
            if random.random() < self.config.trend_probability:
                self.trend_direction = random.choice([-1, 1])
                self.trend_duration = random.uniform(300, 1800)  # 5-30 minutes
                self.logger.debug(f"Starting {'upward' if self.trend_direction > 0 else 'downward'} trend")
        
        # Add random noise
        noise = random.gauss(0, self.config.noise_level * (self.config.max_value - self.config.min_value))
        new_value = self.current_value + noise
        
        # Check for spikes/anomalies
        if random.random() < self.config.spike_probability:
            spike_magnitude = random.uniform(0.5, 1.5)
            spike_direction = random.choice([-1, 1])
            spike_value = (self.config.max_value - self.config.min_value) * spike_magnitude * spike_direction
            new_value += spike_value
            self.logger.info(f"Generated spike: {spike_value:+.2f}")
        
        # Ensure value stays within physical limits (with some tolerance for spikes)
        new_value = max(self.config.min_value * 0.9, min(self.config.max_value * 1.1, new_value))
        
        # Update current value with some smoothing
        smoothing_factor = min(1.0, time_delta / 60)  # Full change over 1 minute
        self.current_value = self.current_value + (new_value - self.current_value) * smoothing_factor
        
        # Determine quality based on various factors
        quality = 1.0
        if abs(self.current_value - sum(self.config.normal_range) / 2) > (self.config.normal_range[1] - self.config.normal_range[0]):
            quality *= 0.9  # Lower quality for values outside normal range
        
        if random.random() < 0.01:  # 1% chance of communication issues
            quality *= random.uniform(0.7, 0.9)
        
        self.last_reading_time = now
        
        return SensorDataPoint(
            machine_id=self.machine_id,
            parameter_id=self.parameter_id,
            value=self.current_value,
            timestamp=now,
            quality=quality
        )


class MockSensorSystem:
    """Mock sensor system manager"""
    
    def __init__(self, update_interval: int = 60):
        self.machines: Dict[str, MockMachine] = {}
        self.sensors: Dict[str, MockSensor] = {}
        self.update_interval = update_interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.data_callbacks: List[Callable[[SensorDataPoint], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default machines
        self._initialize_default_machines()
    
    def _initialize_default_machines(self):
        """Initialize default mock machines and sensors"""
        
        # Production Line A
        production_line = MockMachine(
            machine_id='MACHINE_001',
            name='Production Line A',
            location='Floor 1 - Section A'
        )
        production_line.sensors = {
            'temperature': SensorConfig(
                name='Temperature',
                unit='°C',
                min_value=15.0,
                max_value=70.0,
                normal_range=(25.0, 45.0),
                warning_threshold=60.0,
                alarm_threshold=65.0,
                noise_level=0.03
            ),
            'vibration': SensorConfig(
                name='Vibration',
                unit='Hz',
                min_value=0.0,
                max_value=10.0,
                normal_range=(1.0, 4.0),
                warning_threshold=6.0,
                alarm_threshold=8.0,
                noise_level=0.1
            ),
            'speed': SensorConfig(
                name='Speed',
                unit='RPM',
                min_value=100.0,
                max_value=2000.0,
                normal_range=(800.0, 1500.0),
                warning_threshold=1600.0,
                alarm_threshold=1800.0,
                noise_level=0.02
            ),
            'power': SensorConfig(
                name='Power',
                unit='kW',
                min_value=5.0,
                max_value=50.0,
                normal_range=(15.0, 35.0),
                warning_threshold=40.0,
                alarm_threshold=45.0,
                noise_level=0.05
            )
        }
        
        # Compressor Unit B
        compressor = MockMachine(
            machine_id='MACHINE_002',
            name='Compressor Unit B',
            location='Floor 1 - Utility Room'
        )
        compressor.sensors = {
            'temperature': SensorConfig(
                name='Temperature',
                unit='°C',
                min_value=20.0,
                max_value=85.0,
                normal_range=(35.0, 65.0),
                warning_threshold=75.0,
                alarm_threshold=80.0,
                noise_level=0.04
            ),
            'pressure': SensorConfig(
                name='Pressure',
                unit='PSI',
                min_value=20.0,
                max_value=120.0,
                normal_range=(60.0, 90.0),
                warning_threshold=100.0,
                alarm_threshold=110.0,
                noise_level=0.03
            ),
            'vibration': SensorConfig(
                name='Vibration',
                unit='Hz',
                min_value=0.0,
                max_value=15.0,
                normal_range=(2.0, 8.0),
                warning_threshold=10.0,
                alarm_threshold=12.0,
                noise_level=0.08
            )
        }
        
        # CNC Mill C
        cnc_mill = MockMachine(
            machine_id='MACHINE_003',
            name='CNC Mill C',
            location='Floor 2 - Machining'
        )
        cnc_mill.sensors = {
            'temperature': SensorConfig(
                name='Temperature',
                unit='°C',
                min_value=18.0,
                max_value=60.0,
                normal_range=(25.0, 40.0),
                warning_threshold=50.0,
                alarm_threshold=55.0,
                noise_level=0.02
            ),
            'speed': SensorConfig(
                name='Speed',
                unit='RPM',
                min_value=500.0,
                max_value=4000.0,
                normal_range=(1500.0, 3000.0),
                warning_threshold=3500.0,
                alarm_threshold=3800.0,
                noise_level=0.01
            ),
            'power': SensorConfig(
                name='Power',
                unit='kW',
                min_value=15.0,
                max_value=80.0,
                normal_range=(25.0, 60.0),
                warning_threshold=70.0,
                alarm_threshold=75.0,
                noise_level=0.03
            )
        }
        
        # Add machines to system
        for machine in [production_line, compressor, cnc_mill]:
            self.add_machine(machine)
    
    def add_machine(self, machine: MockMachine):
        """Add a machine to the mock sensor system"""
        self.machines[machine.machine_id] = machine
        
        # Create sensors for this machine
        for param_id, sensor_config in machine.sensors.items():
            sensor_key = f"{machine.machine_id}.{param_id}"
            self.sensors[sensor_key] = MockSensor(machine.machine_id, param_id, sensor_config)
        
        self.logger.info(f"Added machine {machine.machine_id} with {len(machine.sensors)} sensors")
    
    def add_data_callback(self, callback: Callable[[SensorDataPoint], None]):
        """Add a callback function to receive sensor data"""
        self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable[[SensorDataPoint], None]):
        """Remove a callback function"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def start(self):
        """Start the mock sensor system"""
        if self.is_running:
            self.logger.warning("Mock sensor system is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_sensors, daemon=True)
        self.thread.start()
        self.logger.info(f"Started mock sensor system with {len(self.sensors)} sensors")
    
    def stop(self):
        """Stop the mock sensor system"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Stopped mock sensor system")
    
    def _run_sensors(self):
        """Main sensor update loop"""
        while self.is_running:
            try:
                # Generate readings for all sensors
                for sensor in self.sensors.values():
                    if self.machines[sensor.machine_id].is_active:
                        reading = sensor.generate_reading()
                        
                        # Send to all callbacks
                        for callback in self.data_callbacks:
                            try:
                                callback(reading)
                            except Exception as e:
                                self.logger.error(f"Error in data callback: {e}")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in sensor update loop: {e}")
                time.sleep(1)  # Brief pause before retry
    
    def get_current_readings(self) -> List[SensorDataPoint]:
        """Get current readings from all sensors"""
        readings = []
        for sensor in self.sensors.values():
            if self.machines[sensor.machine_id].is_active:
                readings.append(sensor.generate_reading())
        return readings
    
    def get_machine_readings(self, machine_id: str) -> List[SensorDataPoint]:
        """Get current readings for a specific machine"""
        readings = []
        if machine_id in self.machines and self.machines[machine_id].is_active:
            for sensor in self.sensors.values():
                if sensor.machine_id == machine_id:
                    readings.append(sensor.generate_reading())
        return readings
    
    def set_machine_status(self, machine_id: str, is_active: bool):
        """Enable or disable a machine"""
        if machine_id in self.machines:
            self.machines[machine_id].is_active = is_active
            status = "activated" if is_active else "deactivated"
            self.logger.info(f"Machine {machine_id} {status}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_machines = sum(1 for m in self.machines.values() if m.is_active)
        total_sensors = sum(len(m.sensors) for m in self.machines.values())
        active_sensors = sum(len(m.sensors) for m in self.machines.values() if m.is_active)
        
        return {
            'is_running': self.is_running,
            'total_machines': len(self.machines),
            'active_machines': active_machines,
            'total_sensors': total_sensors,
            'active_sensors': active_sensors,
            'update_interval': self.update_interval
        }


# Global mock sensor system instance
mock_sensor_system = MockSensorSystem()


def get_mock_sensor_system() -> MockSensorSystem:
    """Get the global mock sensor system instance"""
    return mock_sensor_system


# Example usage functions
def demo_sensor_output(duration_seconds: int = 60):
    """Demo function to show sensor output for a specified duration"""
    print("NextCare Mock Sensor Demo")
    print("=" * 50)
    
    system = MockSensorSystem(update_interval=5)  # 5-second updates for demo
    
    def print_reading(reading: SensorDataPoint):
        print(f"{reading.timestamp.strftime('%H:%M:%S')} | {reading}")
    
    system.add_data_callback(print_reading)
    system.start()
    
    try:
        time.sleep(duration_seconds)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        system.stop()


if __name__ == "__main__":
    # Run demo
    demo_sensor_output(30)  # 30-second demo