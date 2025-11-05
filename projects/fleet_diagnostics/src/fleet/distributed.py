"""
Distributed system module for fleet-wide operations and telemetry.
Implements service discovery, leader election, and distributed data collection.
"""
import asyncio
import json
import time
import random
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Set
import logging
import hashlib

logger = logging.getLogger(__name__)

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class NodeInfo:
    node_id: str
    address: str
    port: int
    state: NodeState
    last_seen: float
    
    def to_dict(self):
        return {
            **asdict(self),
            "state": self.state.value
        }

@dataclass
class TelemetryData:
    timestamp: float
    node_id: str
    metrics: Dict[str, float]
    
    def to_dict(self):
        return asdict(self)

class ConsensusProtocol:
    """Implementation of Raft-like consensus protocol."""
    def __init__(self, node_id: str, address: str, port: int):
        self.node_id = node_id
        self.address = address
        self.port = port
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.leader_id: Optional[str] = None
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
        self._peers: Dict[str, NodeInfo] = {}
        self._vote_count = 0
        
    async def start(self):
        """Start consensus protocol."""
        asyncio.create_task(self._election_timer())
        asyncio.create_task(self._heartbeat_timer())
        
    async def _election_timer(self):
        """Timer for election timeout."""
        while True:
            await asyncio.sleep(0.1)  # Check frequently
            if (self.state == NodeState.FOLLOWER and 
                time.time() - self.last_heartbeat > self.election_timeout):
                await self._start_election()
                
    async def _start_election(self):
        """Start leader election."""
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self._vote_count = 1
        
        # Request votes from peers
        for peer_id, peer in self._peers.items():
            response = await self._request_vote(peer)
            if response.get("vote_granted"):
                self._vote_count += 1
                
        # Check if we won the election
        if self._vote_count > len(self._peers) / 2:
            self.state = NodeState.LEADER
            self.leader_id = self.node_id
            logger.info(f"Node {self.node_id} became leader")
            
    async def _heartbeat_timer(self):
        """Timer for leader heartbeats."""
        while True:
            await asyncio.sleep(0.5)  # Heartbeat interval
            if self.state == NodeState.LEADER:
                for peer_id, peer in self._peers.items():
                    await self._send_heartbeat(peer)
                    
    async def _request_vote(self, peer: NodeInfo) -> dict:
        """Send vote request to peer."""
        # Simulate network request
        await asyncio.sleep(0.05)
        # Simulate random vote
        return {"vote_granted": random.random() > 0.3}
        
    async def _send_heartbeat(self, peer: NodeInfo):
        """Send heartbeat to peer."""
        # Simulate network request
        await asyncio.sleep(0.05)
        
    def add_peer(self, node_info: NodeInfo):
        """Add peer to known peers."""
        self._peers[node_info.node_id] = node_info

class DistributedTelemetry:
    """Distributed telemetry collection and aggregation."""
    def __init__(self, consensus: ConsensusProtocol):
        self._consensus = consensus
        self._telemetry_buffer: List[TelemetryData] = []
        self._buffer_lock = asyncio.Lock()
        self._aggregated_data: Dict[str, List[float]] = {}
        
    async def submit_telemetry(self, data: TelemetryData):
        """Submit telemetry data to the distributed system."""
        async with self._buffer_lock:
            self._telemetry_buffer.append(data)
            
        if self._consensus.state == NodeState.LEADER:
            # Leader aggregates and distributes data
            await self._aggregate_telemetry()
            
    async def _aggregate_telemetry(self):
        """Aggregate telemetry data across nodes."""
        async with self._buffer_lock:
            if not self._telemetry_buffer:
                return
                
            # Group by metric
            for data in self._telemetry_buffer:
                for metric, value in data.metrics.items():
                    if metric not in self._aggregated_data:
                        self._aggregated_data[metric] = []
                    self._aggregated_data[metric].append(value)
                    
            self._telemetry_buffer.clear()
            
    def get_aggregated_stats(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated statistics for all metrics."""
        import numpy as np
        stats = {}
        for metric, values in self._aggregated_data.items():
            if values:
                stats[metric] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }
        return stats

class FleetManager:
    """High-level fleet management interface."""
    def __init__(self, node_id: str, address: str, port: int):
        self._consensus = ConsensusProtocol(node_id, address, port)
        self._telemetry = DistributedTelemetry(self._consensus)
        self._known_nodes: Set[str] = {node_id}
        
    async def start(self):
        """Start fleet management services."""
        await self._consensus.start()
        asyncio.create_task(self._discovery_service())
        
    async def _discovery_service(self):
        """Service discovery implementation."""
        while True:
            # Simulate network discovery
            await asyncio.sleep(5.0)
            # Simulate finding new nodes
            if random.random() > 0.7:
                new_node_id = f"node_{random.randint(1000, 9999)}"
                if new_node_id not in self._known_nodes:
                    self._known_nodes.add(new_node_id)
                    node_info = NodeInfo(
                        node_id=new_node_id,
                        address=f"10.0.0.{len(self._known_nodes)}",
                        port=8000 + len(self._known_nodes),
                        state=NodeState.FOLLOWER,
                        last_seen=time.time()
                    )
                    self._consensus.add_peer(node_info)
                    
    async def submit_telemetry(self, metrics: Dict[str, float]):
        """Submit telemetry data to the distributed system."""
        data = TelemetryData(
            timestamp=time.time(),
            node_id=self._consensus.node_id,
            metrics=metrics
        )
        await self._telemetry.submit_telemetry(data)
        
    def get_cluster_stats(self) -> Dict[str, Dict[str, float]]:
        """Get aggregated statistics for the cluster."""
        return self._telemetry.get_aggregated_stats()
        
    def is_leader(self) -> bool:
        """Check if this node is the cluster leader."""
        return self._consensus.state == NodeState.LEADER
        
    def get_cluster_size(self) -> int:
        """Get number of known nodes in cluster."""
        return len(self._known_nodes)