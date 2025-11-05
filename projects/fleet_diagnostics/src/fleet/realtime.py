"""Real-time telemetry system for fleet diagnostics.

This module provides hardware interfaces and real-time guarantees for
sensor data collection and anomaly detection.

Timing requirements:
- GPS: 50ms max latency
- Accelerometer: 100Hz (10ms period)
- Temperature: 1Hz
- Anomaly detection: 100ms max latency
"""
import time
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple

# Timing constants (seconds)
GPS_TIMEOUT = 0.050  # 50ms
ACCEL_PERIOD = 0.010  # 10ms (100Hz)
TEMP_PERIOD = 1.0    # 1s
ANOMALY_TIMEOUT = 0.100  # 100ms

@dataclass
class SensorConfig:
    """Configuration for a sensor."""
    name: str
    sample_rate_hz: float
    timeout_seconds: float


class SensorTimeout(Exception):
    """Raised when sensor read exceeds timeout."""
    pass


class RealTimeTelemetry:
    """Real-time telemetry collection with timing guarantees."""
    
    def __init__(self):
        self._sensors = {
            'gps': SensorConfig('GPS', 20.0, GPS_TIMEOUT),
            'accel': SensorConfig('Accelerometer', 100.0, ACCEL_PERIOD),
            'temp': SensorConfig('Temperature', 1.0, TEMP_PERIOD)
        }
        self._last_reads: Dict[str, float] = {}
        
    def configure_sampling_rate(self, sensor_type: str, rate_hz: float) -> None:
        """Configure sensor sampling rate.
        
        Args:
            sensor_type: Sensor name ('gps', 'accel', 'temp')
            rate_hz: Desired sampling rate in Hz
            
        Raises:
            ValueError: If sensor_type unknown or rate invalid
        """
        if sensor_type not in self._sensors:
            raise ValueError(f"Unknown sensor type: {sensor_type}")
        if rate_hz <= 0:
            raise ValueError(f"Invalid rate: {rate_hz}")
            
        sensor = self._sensors[sensor_type]
        sensor.sample_rate_hz = rate_hz
        sensor.timeout_seconds = 1.0 / rate_hz
        
    def read_with_timeout(self, timeout_ms: int) -> Dict[str, float]:
        """Read all due sensors with timeout.
        
        Args:
            timeout_ms: Maximum milliseconds to wait
            
        Returns:
            Dict mapping sensor name to value
            
        Raises:
            SensorTimeout: If timeout exceeded
        """
        deadline = time.perf_counter() + timeout_ms / 1000.0
        results = {}
        
        for name, sensor in self._sensors.items():
            # Check if sensor read is due
            now = time.perf_counter()
            last = self._last_reads.get(name, 0)
            if now - last < 1.0 / sensor.sample_rate_hz:
                continue
                
            # Read with timeout
            if now > deadline:
                raise SensorTimeout(f"Timeout reading {name}")
                
            # Simulate sensor read
            results[name] = self._simulate_read(name)
            self._last_reads[name] = now
            
        return results
    
    def _simulate_read(self, sensor_type: str) -> float:
        """Simulate reading a sensor (replace with real hardware)."""
        time.sleep(0.001)  # Simulate 1ms read time
        return 0.0  # Dummy value


class RealTimeAnomalyDetector:
    """Real-time anomaly detection with timing guarantees."""
    
    def __init__(self, telemetry: RealTimeTelemetry):
        self.telemetry = telemetry
        self._history: Dict[str, List[Tuple[float, float]]] = {}
        
    def update(self, timeout_ms: int) -> Dict[str, bool]:
        """Update anomaly detection with timeout.
        
        Args:
            timeout_ms: Maximum milliseconds to wait
            
        Returns:
            Dict mapping sensor to anomaly boolean
            
        Raises:
            SensorTimeout: If timeout exceeded
        """
        # Read sensors
        t0 = time.perf_counter()
        values = self.telemetry.read_with_timeout(timeout_ms)
        
        # Update histories and check for anomalies
        now = time.perf_counter()
        results = {}
        
        for sensor, value in values.items():
            history = self._history.setdefault(sensor, [])
            history.append((now, value))
            
            # Trim old values (keep 1 minute)
            cutoff = now - 60.0
            while history and history[0][0] < cutoff:
                history.pop(0)
                
            # Check for anomalies (simple threshold check)
            if len(history) >= 2:
                delta = abs(history[-1][1] - history[-2][1])
                results[sensor] = delta > 1.0
                
        # Check timing
        dt = time.perf_counter() - t0
        if dt > ANOMALY_TIMEOUT:
            raise SensorTimeout(
                f"Anomaly detection took {dt*1000:.1f}ms > {ANOMALY_TIMEOUT*1000:.1f}ms"
            )
            
        return results