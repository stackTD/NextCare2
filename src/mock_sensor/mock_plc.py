"""
Mock PLC/Sensor simulator for testing NextCare2 application
"""

import socket
import json
import threading
import time
import random
import math
import logging
from typing import Dict, Any
try:
    from ..utils.constants import SENSOR_HOST, SENSOR_PORT, REGISTER_MAP
except ImportError:
    from utils.constants import SENSOR_HOST, SENSOR_PORT, REGISTER_MAP

logger = logging.getLogger(__name__)

class MockPLC:
    """Mock PLC simulator that responds to TCP requests"""
    
    def __init__(self, host: str = SENSOR_HOST, port: int = SENSOR_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.client_threads = []
        
        # Initialize register values with realistic data
        self.registers = {}
        self._initialize_registers()
        
        # Background thread for data simulation
        self.simulation_thread = None
        
    def _initialize_registers(self):
        """Initialize registers with realistic starting values"""
        for register, config in REGISTER_MAP.items():
            # Start with values in the middle of the range
            mid_value = (config["min"] + config["max"]) / 2
            self.registers[register] = {
                "value": mid_value,
                "base_value": mid_value,
                "trend": 0.0,  # Trend factor for realistic variation
                "noise_factor": 0.1,  # Noise level
                "config": config
            }
        
        logger.info(f"Initialized {len(self.registers)} registers")
    
    def start_server(self):
        """Start the mock PLC server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            
            # Start data simulation thread
            self.simulation_thread = threading.Thread(target=self._simulate_data, daemon=True)
            self.simulation_thread.start()
            
            logger.info(f"Mock PLC server started on {self.host}:{self.port}")
            
            # Accept client connections
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Client connected from {client_address}")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                except socket.error as e:
                    if self.running:  # Only log if we're not shutting down
                        logger.error(f"Error accepting client connection: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start mock PLC server: {e}")
        finally:
            self.stop_server()
    
    def stop_server(self):
        """Stop the mock PLC server"""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Wait for client threads to finish
        for thread in self.client_threads:
            thread.join(timeout=1)
        
        logger.info("Mock PLC server stopped")
    
    def _handle_client(self, client_socket: socket.socket, client_address):
        """Handle individual client connection"""
        try:
            while self.running:
                # Receive data from client
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Parse JSON command
                try:
                    command_str = data.decode('utf-8').strip()
                    command = json.loads(command_str)
                    
                    # Process command and generate response
                    response = self._process_command(command)
                    
                    # Send response
                    response_json = json.dumps(response)
                    client_socket.send(response_json.encode('utf-8') + b'\n')
                    
                except json.JSONDecodeError:
                    # Send error response for invalid JSON
                    error_response = {"status": "error", "message": "Invalid JSON"}
                    response_json = json.dumps(error_response)
                    client_socket.send(response_json.encode('utf-8') + b'\n')
                
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            logger.info(f"Client {client_address} disconnected")
    
    def _process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process command from client and return response"""
        action = command.get("action")
        
        if action == "read":
            register = command.get("register")
            return self._read_register(register)
        
        elif action == "read_multiple":
            registers = command.get("registers", [])
            return self._read_multiple_registers(registers)
        
        elif action == "write":
            register = command.get("register")
            value = command.get("value")
            return self._write_register(register, value)
        
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    def _read_register(self, register: str) -> Dict[str, Any]:
        """Read single register value"""
        if register in self.registers:
            value = self.registers[register]["value"]
            return {
                "status": "ok",
                "register": register,
                "value": round(value, 2)
            }
        else:
            return {
                "status": "error",
                "message": f"Register {register} not found"
            }
    
    def _read_multiple_registers(self, registers: list) -> Dict[str, Any]:
        """Read multiple register values"""
        values = {}
        errors = []
        
        for register in registers:
            if register in self.registers:
                values[register] = round(self.registers[register]["value"], 2)
            else:
                errors.append(f"Register {register} not found")
        
        response = {
            "status": "ok" if not errors else "partial",
            "values": values
        }
        
        if errors:
            response["errors"] = errors
        
        return response
    
    def _write_register(self, register: str, value: float) -> Dict[str, Any]:
        """Write value to register"""
        if register in self.registers:
            # Update the base value for the register
            self.registers[register]["value"] = value
            self.registers[register]["base_value"] = value
            
            return {
                "status": "ok",
                "register": register,
                "value": value
            }
        else:
            return {
                "status": "error",
                "message": f"Register {register} not found"
            }
    
    def _simulate_data(self):
        """Simulate realistic sensor data with trends and noise"""
        start_time = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - start_time
            
            for register, data in self.registers.items():
                config = data["config"]
                base_value = data["base_value"]
                
                # Simulate different patterns based on parameter type
                if "Temperature" in config["name"]:
                    # Temperature with slow sine wave + noise
                    trend = math.sin(elapsed / 60) * 5  # 60 second cycle, ±5 degrees
                    noise = random.gauss(0, 2)  # ±2 degree noise
                    
                elif "Pressure" in config["name"]:
                    # Pressure with occasional spikes
                    trend = math.sin(elapsed / 30) * 1  # 30 second cycle, ±1 bar
                    if random.random() < 0.01:  # 1% chance of spike
                        trend += random.uniform(1, 3)
                    noise = random.gauss(0, 0.1)  # ±0.1 bar noise
                    
                elif "Vibration" in config["name"]:
                    # Vibration with random fluctuations
                    trend = math.sin(elapsed / 10) * 2  # Fast oscillation
                    noise = random.gauss(0, 1)  # ±1 mm/s noise
                    
                elif "Speed" in config["name"]:
                    # Speed with gradual changes
                    trend = math.sin(elapsed / 120) * 100  # 2 minute cycle, ±100 RPM
                    noise = random.gauss(0, 10)  # ±10 RPM noise
                    
                elif "Current" in config["name"]:
                    # Current with load variations
                    trend = math.sin(elapsed / 45) * 5  # 45 second cycle, ±5 A
                    noise = random.gauss(0, 1)  # ±1 A noise
                    
                elif "Voltage" in config["name"]:
                    # Voltage relatively stable
                    trend = math.sin(elapsed / 180) * 10  # 3 minute cycle, ±10 V
                    noise = random.gauss(0, 2)  # ±2 V noise
                    
                else:
                    # Default pattern
                    trend = math.sin(elapsed / 60) * (config["max"] - config["min"]) * 0.1
                    noise = random.gauss(0, (config["max"] - config["min"]) * 0.05)
                
                # Calculate new value
                new_value = base_value + trend + noise
                
                # Clamp to valid range
                new_value = max(config["min"], min(config["max"], new_value))
                
                # Update register value
                data["value"] = new_value
            
            # Sleep for a short interval
            time.sleep(0.5)  # Update every 500ms
    
    def get_register_values(self) -> Dict[str, float]:
        """Get current values of all registers"""
        return {reg: data["value"] for reg, data in self.registers.items()}
    
    def set_register_value(self, register: str, value: float):
        """Manually set a register value"""
        if register in self.registers:
            self.registers[register]["value"] = value
            self.registers[register]["base_value"] = value

def run_mock_plc(host: str = SENSOR_HOST, port: int = SENSOR_PORT):
    """Run the mock PLC server"""
    plc = MockPLC(host, port)
    
    try:
        plc.start_server()
    except KeyboardInterrupt:
        logger.info("Shutting down mock PLC server...")
        plc.stop_server()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run the mock PLC
    run_mock_plc()