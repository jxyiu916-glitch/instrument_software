"""Integration tests for complete system behavior."""
import pytest
import asyncio
import time
import numpy as np
from control.async_control import AsyncControlLoop
from control.firmware import FirmwareManager, FirmwareVersion
from fleet.distributed import FleetManager

class TestSystem:
    """Test fixture representing complete system."""
    def __init__(self):
        self.control = AsyncControlLoop()
        self.firmware = FirmwareManager("/dev/ttyUSB0")
        self.fleet = FleetManager("test_node", "localhost", 8000)
        self._running = False
        
    async def start(self):
        """Start all system components."""
        self._running = True
        await self.firmware.initialize()
        await self.fleet.start()
        await self.control.start()
        
    async def stop(self):
        """Stop all system components."""
        self._running = False
        await self.control.stop()
        
    async def collect_metrics(self):
        """Collect system-wide metrics."""
        if not self._running:
            return {}
            
        metrics = {}
        
        # Get control system metrics
        for sensor_id, buffer in self.control._sensor_buffers.items():
            readings = buffer.get_latest(10)
            if readings:
                values = [r.value for r in readings]
                metrics[f"{sensor_id}_mean"] = float(np.mean(values))
                metrics[f"{sensor_id}_std"] = float(np.std(values))
                
        return metrics

@pytest.fixture
async def system():
    """Fixture providing system instance."""
    sys = TestSystem()
    yield sys
    await sys.stop()

@pytest.mark.asyncio
async def test_system_startup(system):
    """Test complete system startup sequence."""
    await system.start()
    
    # Verify firmware version
    version = await system.firmware.get_version()
    assert isinstance(version, FirmwareVersion)
    
    # Verify control loop
    assert len(system.control._sensor_buffers) > 0
    
    # Verify fleet management
    assert system.fleet.get_cluster_size() >= 1

@pytest.mark.asyncio
async def test_system_telemetry(system):
    """Test end-to-end telemetry collection and aggregation."""
    await system.start()
    
    # Collect and submit metrics
    for _ in range(5):
        metrics = await system.collect_metrics()
        assert len(metrics) > 0
        await system.fleet.submit_telemetry(metrics)
        await asyncio.sleep(0.1)
        
    # Check aggregated stats
    stats = system.fleet.get_cluster_stats()
    assert len(stats) > 0
    
    # Verify stat structure
    for metric, values in stats.items():
        assert "mean" in values
        assert "std" in values
        assert isinstance(values["mean"], float)

@pytest.mark.asyncio
async def test_firmware_update_sequence(system):
    """Test firmware update during normal operation."""
    await system.start()
    
    # Get initial version
    initial_version = await system.firmware.get_version()
    
    # Prepare test firmware
    test_firmware = bytes([0xFF] * 1024)
    new_version = FirmwareVersion(
        initial_version.major,
        initial_version.minor + 1,
        0,
        "testfirmware"
    )
    
    # Perform update while system is running
    await system.firmware.update_firmware(test_firmware, new_version)
    
    # Verify new version
    current_version = await system.firmware.get_version()
    assert current_version == new_version
    
    # Verify system still operational
    metrics = await system.collect_metrics()
    assert len(metrics) > 0

@pytest.mark.asyncio
async def test_control_loop_stability(system):
    """Test control loop stability under various conditions."""
    await system.start()
    
    # Collect baseline metrics
    baseline_metrics = []
    for _ in range(10):
        metrics = await system.collect_metrics()
        baseline_metrics.append(metrics)
        await asyncio.sleep(0.1)
        
    # Calculate stability metrics
    for sensor in ["temp", "pressure", "flow"]:
        values = [m[f"{sensor}_mean"] for m in baseline_metrics if f"{sensor}_mean" in m]
        if values:
            std = np.std(values)
            assert std < 10.0, f"Control loop unstable for {sensor}"

@pytest.mark.asyncio
async def test_fault_tolerance(system):
    """Test system behavior under simulated faults."""
    await system.start()
    
    # Test fleet management fault tolerance
    original_size = system.fleet.get_cluster_size()
    
    # Simulate node additions
    for _ in range(3):
        await asyncio.sleep(1.0)
        new_size = system.fleet.get_cluster_size()
        assert new_size >= original_size
        
    # Verify continued operation
    metrics = await system.collect_metrics()
    assert len(metrics) > 0
    
    # Test control system fault tolerance
    for sensor_id in list(system.control._sensor_buffers.keys()):
        # Simulate sensor failure by clearing buffer
        system.control._sensor_buffers[sensor_id]._buffer.clear()
        
        # Verify system continues with remaining sensors
        await asyncio.sleep(0.5)
        metrics = await system.collect_metrics()
        assert len(metrics) > 0

@pytest.mark.asyncio
async def test_performance_requirements(system):
    """Test system performance and timing requirements."""
    await system.start()
    
    # Measure control loop timing
    start_time = time.time()
    samples = []
    
    for _ in range(100):
        before = time.time()
        metrics = await system.collect_metrics()
        samples.append(time.time() - before)
        await asyncio.sleep(0.01)
        
    duration = time.time() - start_time
    
    # Verify timing constraints
    avg_latency = np.mean(samples)
    max_latency = max(samples)
    
    assert avg_latency < 0.005  # Average latency under 5ms
    assert max_latency < 0.020  # Max latency under 20ms
    
    # Verify throughput
    assert len(samples) / duration >= 50  # At least 50Hz operation