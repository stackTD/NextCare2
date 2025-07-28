"""
TCP sensor communication client
"""

import socket
import json
import threading
import time
import logging
from typing import Dict, Any, Optional, Callable
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
try:
    from ..utils.constants import SENSOR_HOST, SENSOR_PORT, DATA_POLLING_INTERVAL
except ImportError:
    from utils.constants import SENSOR_HOST, SENSOR_PORT, DATA_POLLING_INTERVAL

logger = logging.getLogger(__name__)

class SensorClient(QObject):
    """TCP client for communicating with sensor/PLC simulator"""
    
    # Signals for data updates
    data_received = pyqtSignal(dict)  # Emits {register: value} dictionary
    connection_status_changed = pyqtSignal(bool)  # Emits True/False for connected/disconnected
    error_occurred = pyqtSignal(str)  # Emits error message
    
    def __init__(self, host: str = SENSOR_HOST, port: int = SENSOR_PORT):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self.poll_data)
        self.polling_interval = DATA_POLLING_INTERVAL
        self.register_callbacks = {}
        
    def connect_to_sensor(self) -> bool:
        """Establish connection to sensor/PLC"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            self.connection_status_changed.emit(True)
            logger.info(f"Connected to sensor at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to sensor: {e}")
            self.connected = False
            self.connection_status_changed.emit(False)
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            return False
    
    def disconnect_from_sensor(self):
        """Disconnect from sensor/PLC"""
        self.stop_polling()
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.connected = False
        self.connection_status_changed.emit(False)
        logger.info("Disconnected from sensor")
    
    def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send command to sensor and get response"""
        if not self.connected or not self.socket:
            return None
        
        try:
            # Send command as JSON
            command_json = json.dumps(command)
            self.socket.send(command_json.encode('utf-8') + b'\n')
            
            # Receive response
            response_data = b''
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in chunk:
                    break
            
            if response_data:
                response_json = response_data.decode('utf-8').strip()
                return json.loads(response_json)
            
        except socket.timeout:
            logger.warning("Socket timeout during command send")
            self.error_occurred.emit("Communication timeout")
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            self.error_occurred.emit(f"Communication error: {str(e)}")
            self.disconnect_from_sensor()
        
        return None
    
    def read_register(self, register: str) -> Optional[float]:
        """Read single register value"""
        command = {
            "action": "read",
            "register": register
        }
        
        response = self.send_command(command)
        if response and response.get("status") == "ok":
            return response.get("value")
        
        return None
    
    def read_multiple_registers(self, registers: list) -> Dict[str, float]:
        """Read multiple register values"""
        command = {
            "action": "read_multiple",
            "registers": registers
        }
        
        response = self.send_command(command)
        if response and response.get("status") == "ok":
            return response.get("values", {})
        
        return {}
    
    def write_register(self, register: str, value: float) -> bool:
        """Write value to register"""
        command = {
            "action": "write",
            "register": register,
            "value": value
        }
        
        response = self.send_command(command)
        return response and response.get("status") == "ok"
    
    def start_polling(self, interval: int = None):
        """Start automatic data polling"""
        if interval:
            self.polling_interval = interval
        
        if not self.connected:
            if not self.connect_to_sensor():
                return False
        
        self.polling_timer.start(self.polling_interval)
        logger.info(f"Started polling with interval {self.polling_interval}ms")
        return True
    
    def stop_polling(self):
        """Stop automatic data polling"""
        self.polling_timer.stop()
        logger.info("Stopped polling")
    
    def poll_data(self):
        """Poll data from all registered addresses"""
        if not self.connected:
            return
        
        # Get all register addresses that are being monitored
        from ..database.operations import db_ops
        from ..utils.constants import REGISTER_MAP
        
        # For now, poll all known registers
        registers = list(REGISTER_MAP.keys())
        
        data = self.read_multiple_registers(registers)
        if data:
            self.data_received.emit(data)
        else:
            # If polling fails, try to reconnect
            logger.warning("Polling failed, attempting to reconnect")
            self.disconnect_from_sensor()
            time.sleep(1)  # Brief delay before reconnect attempt
            self.connect_to_sensor()
    
    def is_connected(self) -> bool:
        """Check if connected to sensor"""
        return self.connected
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "host": self.host,
            "port": self.port,
            "connected": self.connected,
            "polling": self.polling_timer.isActive()
        }

class AsyncSensorClient:
    """Threaded sensor client for non-blocking operations"""
    
    def __init__(self, host: str = SENSOR_HOST, port: int = SENSOR_PORT):
        self.host = host
        self.port = port
        self.client = SensorClient(host, port)
        self.thread = None
        self.running = False
    
    def start(self, data_callback: Callable = None, status_callback: Callable = None):
        """Start sensor client in separate thread"""
        if data_callback:
            self.client.data_received.connect(data_callback)
        if status_callback:
            self.client.connection_status_changed.connect(status_callback)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop sensor client"""
        self.running = False
        self.client.stop_polling()
        self.client.disconnect_from_sensor()
        
        if self.thread:
            self.thread.join(timeout=5)
    
    def _run_client(self):
        """Run client in thread"""
        self.client.connect_to_sensor()
        self.client.start_polling()
        
        while self.running:
            time.sleep(0.1)
        
        self.client.stop_polling()
        self.client.disconnect_from_sensor()
    
    def get_client(self) -> SensorClient:
        """Get the underlying sensor client"""
        return self.client

# Global sensor client instance
sensor_client = SensorClient()