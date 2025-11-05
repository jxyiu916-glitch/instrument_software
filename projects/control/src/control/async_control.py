"""
Asynchronous control system implementation with thread-safe interfaces.
Handles concurrent sensor reading, actuator control, and telemetry collection.
"""
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class SensorReading:
    timestamp: float
    value: float
    sensor_id: str
    
class ThreadSafeBuffer:
    """Thread-safe circular buffer for sensor readings."""
    def __init__(self, max_size: int = 1000):
        self._buffer: List[SensorReading] = []
        self._max_size = max_size
        self._lock = threading.Lock()
        
    def add(self, reading: SensorReading) -> None:
        with self._lock:
            self._buffer.append(reading)
            if len(self._buffer) > self._max_size:
                self._buffer.pop(0)
                
    def get_latest(self, n: int = 1) -> List[SensorReading]:
        with self._lock:
            return self._buffer[-n:]

class AsyncControlLoop:
    """Asynchronous control loop with concurrent sensor processing."""
    def __init__(self):
        self._running = False
        self._sensor_buffers: Dict[str, ThreadSafeBuffer] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._control_lock = threading.Lock()
        
    async def start(self):
        """Start the async control loop."""
        self._running = True
        await asyncio.gather(
            self._sensor_polling_task(),
            self._control_task(),
            self._telemetry_task()
        )
        
    async def _sensor_polling_task(self):
        """Concurrent sensor polling task."""
        while self._running:
            # Simulate concurrent sensor reads
            sensor_futures = []
            for sensor_id in ["temp", "pressure", "flow"]:
                future = self._executor.submit(self._read_sensor, sensor_id)
                sensor_futures.append(future)
                
            # Wait for all sensor reads to complete
            for future in sensor_futures:
                reading = await asyncio.wrap_future(future)
                if reading:
                    self._sensor_buffers.setdefault(
                        reading.sensor_id, 
                        ThreadSafeBuffer()
                    ).add(reading)
                    
            await asyncio.sleep(0.01)  # 100Hz polling
            
    def _read_sensor(self, sensor_id: str) -> Optional[SensorReading]:
        """Thread-safe sensor reading simulation."""
        import time
        value = np.random.normal(100, 5)  # Simulate sensor noise
        return SensorReading(
            timestamp=time.time(),
            value=value,
            sensor_id=sensor_id
        )
        
    async def _control_task(self):
        """Main control loop with thread-safe state updates."""
        while self._running:
            with self._control_lock:
                # Get latest readings from all sensors
                readings = {}
                for sensor_id, buffer in self._sensor_buffers.items():
                    latest = buffer.get_latest()
                    if latest:
                        readings[sensor_id] = latest[0]
                        
                # Compute control action (PID simulation)
                if readings:
                    control_action = self._compute_control_action(readings)
                    await self._apply_control(control_action)
                    
            await asyncio.sleep(0.02)  # 50Hz control loop
            
    def _compute_control_action(self, readings: Dict[str, SensorReading]) -> float:
        """Thread-safe control computation."""
        # Simplified PID control simulation
        with self._control_lock:
            return sum(reading.value for reading in readings.values()) / len(readings)
            
    async def _apply_control(self, action: float):
        """Apply control action with proper locking."""
        with self._control_lock:
            # Simulate actuator command
            await asyncio.sleep(0.001)  # Simulate actuator delay
            
    async def _telemetry_task(self):
        """Concurrent telemetry collection."""
        while self._running:
            # Collect telemetry from all buffers
            telemetry = {}
            for sensor_id, buffer in self._sensor_buffers.items():
                telemetry[sensor_id] = buffer.get_latest(10)  # Last 10 readings
                
            # Process telemetry (simulate network send)
            await self._send_telemetry(telemetry)
            await asyncio.sleep(0.1)  # 10Hz telemetry
            
    async def _send_telemetry(self, telemetry: Dict[str, List[SensorReading]]):
        """Simulate async telemetry transmission."""
        await asyncio.sleep(0.005)  # Simulate network latency
        
    async def stop(self):
        """Stop all async tasks."""
        self._running = False
        self._executor.shutdown(wait=True)