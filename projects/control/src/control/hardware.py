"""Hardware abstraction layer for control system.

This module provides register-level access to the control system hardware
and enforces real-time constraints for the control loop.

Register map documented in docs/hardware_interface.md
"""
from dataclasses import dataclass
import struct
import time
from typing import Optional

# Register offsets
REG_MODE = 0x00
REG_SETPOINT = 0x04
REG_CURRENT = 0x08
REG_OUTPUT = 0x0C
REG_STATUS = 0x10
REG_KP = 0x14
REG_KI = 0x18
REG_KD = 0x1C

# Status bits
STATUS_ACTIVE = 1 << 0
STATUS_ERROR = 1 << 1
STATUS_SATURATED = 1 << 2
STATUS_CONVERGED = 1 << 3

# Timing constants (all in seconds)
CONTROL_PERIOD = 0.001  # 1ms control loop
SENSOR_TIMEOUT = 0.0002  # 200μs
OUTPUT_TIMEOUT = 0.00015  # 150μs
ERROR_TIMEOUT = 0.00005  # 50μs


@dataclass
class ControlHardwareConfig:
    """Configuration for control hardware."""
    base_addr: int = 0x1000_0000
    simulate: bool = True  # True to use simulation


class HardwareException(Exception):
    """Raised for hardware-related errors."""
    pass


class TimingException(Exception):
    """Raised when timing constraints are violated."""
    pass


class HardwareInterface:
    """Hardware abstraction layer for control system."""

    def __init__(self, config: Optional[ControlHardwareConfig] = None):
        self.config = config or ControlHardwareConfig()
        self._last_tick = 0.0
        self._simulated_values = {
            REG_MODE: 0,
            REG_SETPOINT: 0.0,
            REG_CURRENT: 0.0,
            REG_OUTPUT: 0.0,
            REG_STATUS: 0,
            REG_KP: 0.0,
            REG_KI: 0.0,
            REG_KD: 0.0,
        }

    def read_register(self, offset: int) -> int:
        """Read a 32-bit register value.
        
        Args:
            offset: Register offset from base address.
            
        Returns:
            32-bit register value.
            
        Raises:
            HardwareException: On hardware error or timeout.
            TimingException: If timing constraints violated.
        """
        t0 = time.perf_counter()
        try:
            if self.config.simulate:
                val = self._simulated_values.get(offset, 0)
            else:
                # Real hardware would use ctypes or similar
                raise NotImplementedError("Real hardware not implemented")
            
            dt = time.perf_counter() - t0
            if dt > SENSOR_TIMEOUT:
                raise TimingException(f"Register read took {dt*1e6:.1f}μs > {SENSOR_TIMEOUT*1e6}μs")
            return val
            
        except Exception as e:
            if not isinstance(e, (HardwareException, TimingException)):
                raise HardwareException(f"Hardware error: {e}") from e
            raise

    def write_register(self, offset: int, value: int) -> None:
        """Write a 32-bit register value.
        
        Args:
            offset: Register offset from base address.
            value: 32-bit value to write.
            
        Raises:
            HardwareException: On hardware error or timeout.
            TimingException: If timing constraints violated.
        """
        t0 = time.perf_counter()
        try:
            if self.config.simulate:
                self._simulated_values[offset] = value
            else:
                # Real hardware would use ctypes or similar
                raise NotImplementedError("Real hardware not implemented")
                
            dt = time.perf_counter() - t0
            if dt > OUTPUT_TIMEOUT:
                raise TimingException(f"Register write took {dt*1e6:.1f}μs > {OUTPUT_TIMEOUT*1e6}μs")
                
        except Exception as e:
            if not isinstance(e, (HardwareException, TimingException)):
                raise HardwareException(f"Hardware error: {e}") from e
            raise

    def read_float(self, offset: int) -> float:
        """Read a float32 value from a register."""
        val = self.read_register(offset)
        return struct.unpack('f', struct.pack('I', val))[0]

    def write_float(self, offset: int, value: float) -> None:
        """Write a float32 value to a register."""
        val = struct.unpack('I', struct.pack('f', value))[0]
        self.write_register(offset, val)

    def wait_next_tick(self) -> None:
        """Wait for next control loop tick.
        
        Raises:
            TimingException: If loop period violated.
        """
        now = time.perf_counter()
        if self._last_tick > 0:
            period = now - self._last_tick
            if abs(period - CONTROL_PERIOD) > 0.00005:  # 50μs jitter tolerance
                raise TimingException(
                    f"Control loop period {period*1e3:.3f}ms deviated from {CONTROL_PERIOD*1e3:.3f}ms"
                )
        
        # Sleep until next tick
        target = self._last_tick + CONTROL_PERIOD
        if target > now:
            time.sleep(target - now)
        self._last_tick = time.perf_counter()


class RealTimeControl:
    """Real-time control loop implementation."""

    def __init__(self, hw: HardwareInterface):
        self.hw = hw
        
    def run_loop(self, max_iterations: Optional[int] = None) -> None:
        """Run the control loop with real-time constraints.
        
        Args:
            max_iterations: Optional maximum iterations (None for infinite).
        """
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            try:
                self.hw.wait_next_tick()
                
                # Read inputs
                t0 = time.perf_counter()
                current = self.hw.read_float(REG_CURRENT)
                setpoint = self.hw.read_float(REG_SETPOINT)
                mode = self.hw.read_register(REG_MODE)
                
                # Compute control law
                if mode == 1:  # PID mode
                    kp = self.hw.read_float(REG_KP)
                    ki = self.hw.read_float(REG_KI)
                    kd = self.hw.read_float(REG_KD)
                    # ... compute PID output ...
                    output = kp * (setpoint - current)  # P-only for demo
                else:
                    output = 0.0
                    
                # Check compute time
                dt = time.perf_counter() - t0
                if dt > 0.0002:  # 200μs compute budget
                    raise TimingException(f"Control compute took {dt*1e6:.1f}μs > 200μs")
                
                # Write output
                self.hw.write_float(REG_OUTPUT, output)
                
                iteration += 1
                
            except Exception as e:
                # Set error status and re-raise
                try:
                    status = self.hw.read_register(REG_STATUS)
                    self.hw.write_register(REG_STATUS, status | STATUS_ERROR)
                except Exception:
                    pass  # Don't mask original error
                raise