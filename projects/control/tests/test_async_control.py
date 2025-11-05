"""Tests for async control system components."""
import asyncio
import pytest
import numpy as np
from ..src.control.async_control import (
    AsyncControlLoop,
    ThreadSafeBuffer,
    SensorReading
)

@pytest.fixture
def buffer():
    return ThreadSafeBuffer(max_size=100)

@pytest.fixture
def control_loop():
    return AsyncControlLoop()

def test_thread_safe_buffer(buffer):
    # Test concurrent access to buffer
    import threading
    import time
    
    def writer():
        for i in range(50):
            reading = SensorReading(
                timestamp=time.time(),
                value=float(i),
                sensor_id="test"
            )
            buffer.add(reading)
            time.sleep(0.001)
            
    def reader():
        for _ in range(50):
            readings = buffer.get_latest(10)
            assert all(isinstance(r, SensorReading) for r in readings)
            time.sleep(0.001)
            
    # Create concurrent threads
    threads = [
        threading.Thread(target=writer),
        threading.Thread(target=reader)
    ]
    
    # Run threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    # Verify buffer size constraints
    assert len(buffer._buffer) <= 100

@pytest.mark.asyncio
async def test_async_control_loop(control_loop):
    # Start control loop
    task = asyncio.create_task(control_loop.start())
    
    # Let it run for a bit
    await asyncio.sleep(0.5)
    
    # Stop control loop
    await control_loop.stop()
    await task
    
    # Verify sensor buffers were populated
    assert len(control_loop._sensor_buffers) == 3  # temp, pressure, flow
    
    # Check buffer contents
    for buffer in control_loop._sensor_buffers.values():
        readings = buffer.get_latest(10)
        assert len(readings) > 0
        assert all(isinstance(r, SensorReading) for r in readings)
        
        # Verify timestamps are monotonic
        timestamps = [r.timestamp for r in readings]
        assert all(t1 <= t2 for t1, t2 in zip(timestamps[:-1], timestamps[1:]))

@pytest.mark.asyncio
async def test_control_loop_timing(control_loop):
    # Test that control loop maintains timing constraints
    import time
    
    start_time = time.time()
    
    # Run for 1 second
    task = asyncio.create_task(control_loop.start())
    await asyncio.sleep(1.0)
    await control_loop.stop()
    await task
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Verify approximate timing
    for sensor_id, buffer in control_loop._sensor_buffers.items():
        readings = buffer.get_latest(100)
        
        # Calculate average time between readings
        timestamps = [r.timestamp for r in readings]
        intervals = np.diff(timestamps)
        avg_interval = np.mean(intervals)
        
        # Verify sensor polling rate (~100Hz)
        assert 0.008 <= avg_interval <= 0.012  # 10ms ± 2ms
        
    # Verify total runtime
    assert 0.9 <= duration <= 1.1  # 1s ± 0.1s