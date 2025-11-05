"""Tests for distributed system components."""
import os
import sys
import pytest
import asyncio
import time

# ensure local src/ is importable during tests
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from fleet.distributed import (
    FleetManager,
    NodeState,
    NodeInfo,
    TelemetryData,
    ConsensusProtocol,
    DistributedTelemetry
)

@pytest.fixture
def consensus_protocol():
    return ConsensusProtocol("node_1", "localhost", 8000)

@pytest.fixture
def distributed_telemetry(consensus_protocol):
    return DistributedTelemetry(consensus_protocol)

@pytest.fixture
def fleet_manager():
    return FleetManager("node_1", "localhost", 8000)

def test_node_info_serialization():
    node = NodeInfo(
        node_id="test_node",
        address="localhost",
        port=8000,
        state=NodeState.FOLLOWER,
        last_seen=123.45
    )
    data = node.to_dict()
    assert data["node_id"] == "test_node"
    assert data["state"] == "follower"

def test_telemetry_data_serialization():
    data = TelemetryData(
        timestamp=123.45,
        node_id="test_node",
        metrics={"cpu": 0.5, "memory": 0.7}
    )
    serialized = data.to_dict()
    assert serialized["node_id"] == "test_node"
    assert serialized["metrics"]["cpu"] == 0.5

@pytest.mark.asyncio
async def test_consensus_protocol(consensus_protocol):
    # Add some peers
    for i in range(2, 4):
        peer = NodeInfo(
            node_id=f"node_{i}",
            address="localhost",
            port=8000 + i,
            state=NodeState.FOLLOWER,
            last_seen=time.time()
        )
        consensus_protocol.add_peer(peer)
        
    # Start consensus
    await consensus_protocol.start()
    
    # Wait for potential state changes
    await asyncio.sleep(2.0)
    
    # Verify basic properties
    assert consensus_protocol.current_term >= 0
    assert consensus_protocol.state in NodeState
    
    # Verify peer management
    assert len(consensus_protocol._peers) == 2

@pytest.mark.asyncio
async def test_distributed_telemetry(distributed_telemetry):
    # Submit some test data
    for i in range(3):
        data = TelemetryData(
            timestamp=time.time(),
            node_id=f"node_{i}",
            metrics={
                "cpu": 0.5 + i * 0.1,
                "memory": 0.7 + i * 0.1
            }
        )
        await distributed_telemetry.submit_telemetry(data)
        
    # Force aggregation
    await distributed_telemetry._aggregate_telemetry()
    
    # Check statistics
    stats = distributed_telemetry.get_aggregated_stats()
    assert "cpu" in stats
    assert "memory" in stats
    assert all(key in stats["cpu"] for key in ["mean", "std", "min", "max"])

@pytest.mark.asyncio
async def test_fleet_manager(fleet_manager):
    # Start fleet manager
    await fleet_manager.start()
    
    # Submit some telemetry
    for _ in range(3):
        await fleet_manager.submit_telemetry({
            "cpu": 0.5,
            "memory": 0.7,
            "temperature": 45.0
        })
        await asyncio.sleep(0.1)
        
    # Check cluster status
    assert fleet_manager.get_cluster_size() >= 1
    assert isinstance(fleet_manager.is_leader(), bool)
    
    # Check statistics
    stats = fleet_manager.get_cluster_stats()
    if stats:  # Stats might be empty if node is not leader
        assert all(key in stats for key in ["cpu", "memory", "temperature"])