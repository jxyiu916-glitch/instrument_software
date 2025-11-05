"""Core application functionality and shared utilities."""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status states."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class SystemMetrics:
    """System-wide metrics."""
    cpu_usage: float
    memory_usage: float
    uptime: float
    error_count: int
    
    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "uptime": self.uptime,
            "error_count": self.error_count
        }

class SystemMonitor:
    """System-wide monitoring."""
    
    def __init__(self):
        self._status = SystemStatus.STARTING
        self._metrics: Optional[SystemMetrics] = None
        self._subscribers: List[asyncio.Queue] = []
        
    @property
    def status(self) -> SystemStatus:
        """Get current system status."""
        return self._status
        
    @property
    def metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics."""
        return self._metrics
        
    async def start(self):
        """Start system monitoring."""
        self._status = SystemStatus.RUNNING
        asyncio.create_task(self._metrics_collector())
        
    async def stop(self):
        """Stop system monitoring."""
        self._status = SystemStatus.STOPPING
        self._metrics = None
        
    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to metric updates."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue
        
    async def _metrics_collector(self):
        """Collect system metrics periodically."""
        while self._status == SystemStatus.RUNNING:
            try:
                # Simulate metric collection
                self._metrics = SystemMetrics(
                    cpu_usage=0.5,
                    memory_usage=0.3,
                    uptime=100.0,
                    error_count=0
                )
                
                # Notify subscribers
                for queue in self._subscribers:
                    await queue.put(self._metrics.to_dict())
                    
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                self._status = SystemStatus.ERROR
                break
                
            await asyncio.sleep(1.0)  # Collect every second
